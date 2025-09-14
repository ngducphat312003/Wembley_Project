from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6 import QtCore
from PyQt6.QtGui import QImage, QPixmap
from pathlib import Path
import torch
import cv2
from PIL import Image
from collections import Counter
import os
import time
import numpy as np



class Task2Worker(QThread):
    bad = pyqtSignal(int,object)  # Chỉ truyền pixmap
    good = pyqtSignal(object)  # Chỉ truyền pixmap
    time = pyqtSignal(float)
    pos1 = pyqtSignal(list)
    pos2 = pyqtSignal(list)
    finished1 = pyqtSignal(list)

    def __init__(self, dashboard, result, paraconfirm, main):
        super().__init__()
        self.dashboard = dashboard
        self.result = result
        self.paraconfirm = paraconfirm
        self.main = main
        
    def run(self):
        print("Starting task 2...")
        self.StartTime = time.time()
        self.DefectiveTime = []
        # Thêm phần code xử lý Task2 vào đây
        self.dashboard.Backbone.eval()
        results_counter = Counter()
        # Đường dẫn đến thư mục cần kiểm tra
        test_path = Path(r"ImagesResult")
        print(f"Processing images in: {test_path}")
        # Dictionary cho các loại plastic và ngưỡng tương ứng
        plastic_config = {
            "blplastic_": (self.dashboard.MemoryBL, self.dashboard.ScoreBL[0], self.dashboard.pca_bl),
            "brplastic_": (self.dashboard.MemoryBR, self.dashboard.ScoreBR[0], self.dashboard.pca_br),
            "midplastic_": (self.dashboard.MemoryMID, self.dashboard.ScoreMID[0], self.dashboard.pca_mid),
            "tlplastic_": (self.dashboard.MemoryTL, self.dashboard.ScoreTL[0], self.dashboard.pca_tl),
            "trplastic_": (self.dashboard.MemoryTR, self.dashboard.ScoreTR[0], self.dashboard.pca_tr),
        }
        # plastic_config = {
        #     "blplastic_": (self.dashboard.MemoryBL, self.dashboard.ScoreBL[0]),
        #     "brplastic_": (self.dashboard.MemoryBR, self.dashboard.ScoreBR[0]),
        #     "midplastic_": (self.dashboard.MemoryMID, self.dashboard.ScoreMID[0]),
        #     "tlplastic_": (self.dashboard.MemoryTL, self.dashboard.ScoreTL[0]),
        #     "trplastic_": (self.dashboard.MemoryTR, self.dashboard.ScoreTR[0]),
        # }
        self.count_bad = 0
        # Lặp qua tất cả các tệp .jpg trong thư mục
        
        for path in test_path.glob('*.bmp'):
            file_path = str(path)
            print(f"Processing file: {file_path}")
            img = cv2.imread(file_path)
            #Kiểm tra tên của label_56 UI
            if not self.main.label_56.text().startswith("BLACK"):
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            h, w = img.shape[:2]
            # ===== Tô trắng bốn góc ảnh =====
            triangles = [
                ([int(h / 3.25), 0], [0, 0], [0, int(w / 3.25)]),  # Trên trái
                ([0, int(2 * h / 2.75)], [0, h], [int(w / 3.25), h]),  # Dưới trái
                ([w, int(h / 3)], [w, 0], [int(2 * w / 2.75), 0]),  # Trên phải
                ([int(2 * w / 2.75), h], [w, h], [w, int(2 * h / 2.75)])  # Dưới phải
            ]
            for pts in triangles:
                cv2.fillPoly(img, [np.array(pts, np.int32).reshape((-1, 1, 2))], (255, 255, 255))
            # Chuyển từ BGR sang RGB, sau đó sang PIL để biến đổi
            pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            test_image = self.dashboard.Transform(pil_image).cuda().unsqueeze(0)
            # Xác định loại plastic và thực hiện dự đoán

            for plastic, (memory_bank, threshold, pca) in plastic_config.items():
                if plastic in path.name:
                    with torch.no_grad():
                        features = self.dashboard.Backbone(test_image)
                        features1_np = features.cpu().numpy()
                        features1_pca = pca.transform(features1_np)  # Không dùng .fit_transform ở đây!
                        features1_pca_tensor = torch.tensor(features1_pca).cuda()

                        # distances = torch.cdist(features, memory_bank, p=2.0)
                        distances = torch.cdist(features1_pca_tensor, memory_bank, p=2.0)
                        s_star = torch.max(torch.min(distances, dim=1).values)
                        y_score_image = s_star.cpu().numpy()
                        y_pred_image = 1 * (y_score_image >= threshold)
                        class_label = ['GOOD', 'BAD']
                        if class_label[y_pred_image] == 'BAD':
                            results_counter[class_label[y_pred_image]] += 1
                            # Load the image
                            image = cv2.imread(str(path))
                            #Lấy vị trí của ống tương ứng với tên file
                            for image_path, pos in self.result:
                                if path.name == image_path:
                                    print("image_path_bad:",image_path)
                                    self.pos1.emit(pos)
                                    self.DefectiveTime.append(QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss"))
                                    # print("pos_bad: ",pos)
                                    print("Score: ",y_score_image)
                                    cv2.imwrite(os.path.join(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembleyImage\ErrorSave", image_path), image)

                            text = class_label[y_pred_image]
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(image, text, (10, 30), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
                            
                            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            height, width, channel = frame.shape
                            bytes_per_line = 3 * width
                            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                            pixmap = QPixmap.fromImage(q_image)
                            scaled_pixmap = pixmap.scaled(274, 243, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            self.bad.emit(results_counter['BAD'],scaled_pixmap)
                            t7 = time.time()
                            self.time.emit(t7 - self.StartTime)
                            os.remove(path)
                            

                        elif class_label[y_pred_image] == 'GOOD':
                            image = cv2.imread(str(path))
                            for image_path, pos in self.result:
                                if path.name == image_path:
                                    # print("image_path_good",image_path)
                                    self.pos2.emit(pos)
                                    # print("pos_good",pos)
                                    # print("Score: ",y_score_image)
                                    
                            text = class_label[y_pred_image]
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(image, text, (10, 30), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
                            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            height, width, channel = frame.shape
                            bytes_per_line = 3 * width
                            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                            pixmap = QPixmap.fromImage(q_image)
                            scaled_pixmap = pixmap.scaled(274, 243, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            self.good.emit(scaled_pixmap)
                            t7 = time.time()
                            self.time.emit(t7 - self.StartTime)
                            os.remove(path)
                    break  # Thoát vòng lặp khi đã xác định được loại plastic
        t8 = time.time()
        print(f'Once Processing. ({t8 - self.StartTime:.3f}s)')
        self.finished1.emit(self.DefectiveTime)           
        
        





