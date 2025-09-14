from PyQt6.QtCore import QThread, pyqtSignal, Qt 
from PyQt6.QtGui import QImage, QPixmap, QTransform
from PyQt6 import QtCore
from page_Initial import PageInitialBackend
from MainUI1 import Ui_MainWindow
import os
from CubeDetection import run_inference
import cv2
from worker_task1 import Task1Worker
from worker_task2 import Task2Worker
import numpy as np
from math import sqrt
import time
from pymelsec.constants import DT
from pymelsec.tag import Tag



class CaptureAndDetectWorker(QThread):
    finished = pyqtSignal(list,list, list, str)

    def __init__(self, dashboard, initial: PageInitialBackend, main: Ui_MainWindow, paraconfirm, model, device, half, stride, imgsz, opt, image_directory):
        super().__init__()
        self.dashboard = dashboard 
        self.initial = initial
        self.paraconfirm = paraconfirm
        self.model = model
        self.device = device
        self.half = half
        self.stride = stride
        self.imgsz = imgsz
        self.opt = opt
        self.image_directory = image_directory
        self.prediction = False
        self.main = main
        
        self.img = None
       
        self.detected_circles_model = None
        self.Shortage_Time = None
        self.Defective_Time = None
    def run(self):
        self.result = []
        self.pos = []
        self.filename = []
        self.bad_pos = []
        self.shortage_pos = []
        self.shortage_pos_rubber = []
        self.col_save = []
        self.row_save = []
        image_input = r"SourceImages"
        self.image_output = r"ImagesResult"
    
        #Lấy file ảnh jpg trong SourceImages
        image_input1 = os.path.join(image_input, [f for f in os.listdir(image_input) if f.endswith('.bmp')][0])
        self.img = cv2.imread(image_input1)
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)    
        img_blur = cv2.GaussianBlur(img_gray, (5,5), 0)
        self.detected_circles_model = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, dp=float(self.main.leditDp.text()), minDist=int(self.main.leditMinDist.text()),
                                 param1=int(self.main.leditParam1.text()), param2=int(self.main.leditParam2.text()), minRadius=int(self.main.leditMinradius.text()), maxRadius=int(self.main.leditMaxradius.text()))

        pipes_count_model = 0
        bbox_width = 125
        bbox_height = 125
        y_arr = []
        distance_tuples = []
        distance_tuples1 = []
        row = []
        col = []
        self.bbox1 = []
        
        def process_detected_circles(detected_circles_model):
            if detected_circles_model is not None:
                detected_circles = np.uint16(np.around(self.detected_circles_model))
                detected_circles = sorted(detected_circles[0, :], key=lambda x: (x[0], x[1]))
                return detected_circles
            return []

        detected_circles = process_detected_circles(self.detected_circles_model)
        pipes_count_model = len(detected_circles)
        print("Total number of pipes:", pipes_count_model)
        if pipes_count_model < 90:
            print("Not enough pipes detected.")
            self.dashboard.Total += 100
            self.main.lbTotal.setText(str(self.dashboard.Total))
            height, width, channel = self.img.shape
            bytes_per_line = 3 * width
            q_image = QImage(self.img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(850, 445, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            #Xoay 180 độ ảnh 
            scaled_pixmap = scaled_pixmap.transformed(QTransform().rotate(180))
            self.main.lbGeneralImage.setPixmap(scaled_pixmap)
            os.remove(image_input1)
            self.finished.emit([], [], [], "")
            return
        for points in detected_circles:
            a, b, r = points[0], points[1], points[2]
            cv2.circle(self.img, (a, b), 1, (0, 0, 255), 3)
        if self.detected_circles_model is not None:
            detected_circles = np.uint16(np.around(self.detected_circles_model))
            for i, (x, y, _) in enumerate(detected_circles[0, :]):
                distance = sqrt((int(x))**2 + (int(y)**2))
                distance_tuples.append((distance, int(x), int(y)))
            print("length of distance_tuples:", len(distance_tuples1))
            
            while len(distance_tuples1) != 10:
                distance_tuples.sort()
                xmin = min(distance_tuples, key=lambda d: d[0])[1]
                min_y_tuple = min(distance_tuples, key=lambda x: x[2])
                max_x_tuple = max(distance_tuples, key=lambda x: x[1])
                max_x = max_x_tuple[1]
                min_y = min_y_tuple[2]
                min_x_tuple = min(distance_tuples, key=lambda x: x[1])
                min_x = min_x_tuple[1]
                # print("Xmin: ", min_x)
                # print("Ymin: ", min_y)
                # print("Xmax: ", max_x)

                # Filter circles within the x-range and store them
                distance_tuples1 = [(d, x, y) for d, x, y in distance_tuples if xmin - 80 <= x <= xmin + 80]
                distance_tuples1.sort()
                if (distance_tuples1[0][2]< min_y - 50) or (distance_tuples1[0][2]> min_y + 50):
                    print("Vị trí ống đầu tiên bị thiếu")
                    #Lấy giá trị cột 1
                    y_arr = [int(y[2]) for y in distance_tuples1]  # Lấy giá trị y từ distance_tuples1
                    # Tính khoảng cách giữa các phần tử liên tiếp
                    y_distances = [abs(y2 - y1) for y1, y2 in zip(y_arr, y_arr[1:])]
                    x_avg = sum([x[1] for x in distance_tuples1]) / len(distance_tuples1) if distance_tuples1 else 0
                    # Tính khoảng cách trung bình
                    average_distance = sum(y_distances) / len(y_distances) if y_distances else 0
                    # print("Khoảng cách giữa các phần tử liên tiếp:", y_distances)
                    # print("Khoảng cách trung bình:", average_distance)
                    filtered_distances = [d for d in y_distances if d <= average_distance + 70]
                    new_average_distance = sum(filtered_distances) / len(filtered_distances) if filtered_distances else 0
                    y_new = distance_tuples1[0][2] - new_average_distance
                    distance_new = sqrt((int(x_avg))**2 + (int(y_new)**2))
                    # cv2.circle(img, (int(x_avg), int(y_new)), 1, (0, 100, 255), 3)
                    distance_tuples.append((distance_new, int(x_avg), int(y_new)))
                    distance_tuples1.append((distance_new, int(x_avg), int(y_new)))
                    distance_tuples1.sort()
                else:    
                    print("Vị trí ống đầu tiên không bị thiếu")
                    y_arr = [int(y[2]) for y in distance_tuples1]  # Lấy giá trị y từ distance_tuples1
                    # Tính khoảng cách giữa các phần tử liên tiếp
                    y_distances = [abs(y2 - y1) for y1, y2 in zip(y_arr, y_arr[1:])]
                    x_avg = sum([x[1] for x in distance_tuples1]) / len(distance_tuples1) if distance_tuples1 else 0
                    # Tính khoảng cách trung bình
                    average_distance = sum(y_distances) / len(y_distances) if y_distances else 0
                    # print("Khoảng cách giữa các phần tử liên tiếp:", y_distances)
                    # print("Khoảng cách trung bình:", average_distance)
                    # Lọc ra các khoảng cách lớn hơn trung bình và lưu vị trí
                    greater_than_avg = [(i, d) for i, d in enumerate(y_distances) if d > average_distance+70]
                    # Tạo danh sách mới, chỉ giữ các khoảng cách không vượt quá (average_distance + 40)
                    filtered_distances = [d for d in y_distances if d <= average_distance + 70]
                    # Tính lại khoảng cách trung bình mới
                    new_average_distance = sum(filtered_distances) / len(filtered_distances) if filtered_distances else 0
                    # print("Khoảng cách trung bình mới (loại bỏ outlier):", new_average_distance)
                    if greater_than_avg:
                        for i, d in greater_than_avg:
                            # print(f"Khoảng cách lớn hơn trung bình tại vị trí {i}: {d}")
                            y_new = distance_tuples1[i][2] + new_average_distance
                            distance_new = sqrt((int(x_avg))**2 + (int(y_new)**2))
                            # cv2.circle(img, (int(x_avg), int(y_new)), 1, (0, 100, 255), 3)
                            distance_tuples.append((distance_new, int(x_avg), int(y_new)))
                            distance_tuples1.append((distance_new, int(x_avg), int(y_new)))
                            distance_tuples1.sort()
                    elif len(y_distances) != 9:
                        # print("Tô ở vị trí thứ còn thiếu cuối cùng")
                        y_last = distance_tuples1[-1][2] + new_average_distance
                        # cv2.circle(img, (int(x_avg), int(y_last)), 1, (0, 100, 255), 3)
                        distance_new = sqrt((int(x_avg))**2 + (int(y_last)**2))
                        distance_tuples.append((distance_new, int(x_avg), int(y_last)))
                        distance_tuples1.append((distance_new, int(x_avg), int(y_last)))
                        distance_tuples1.sort()
            # print("distance_tuples1",distance_tuples1)
            k = 0
            position = []
            while k < 10:
                count = 0 
                col_search = distance_tuples1[k][2]
                # print("col_search: ",col_search)
                # print("k: ",k)
                col_search_new = col_search
                while count != 10:
                    for d, x, y in distance_tuples: 
                        #Số 60 ở đây là khoảng cách giữa các ống           
                        if (col_search_new - 100 <= y <= col_search_new + 100):
                            count +=1
                            distance_new1 = np.sqrt((int(x))**2 + (int(y))**2)
                            # print("distance_new1: ",distance_new1)
                            # cv2.circle(img, (int(x), int(y)), 3, (200, 100, 255), 3)
                            position.append((float(distance_new1), int(x), int(y)))
                            col_search_new = y
                    position.sort()
                    # print("Count: ", count) 
                    # print("x_search: ",[x[1] for x in position])
                    # print(len(position))
                    if count != 10:
                        # print("Vị trí: ", k+1, " không đủ 10 ống")
                        y_avg1 = sum([y[2] for y in position]) / len(position) if position else 0
                        # print("y_avg1: ", y_avg1)
                        x_distances1 = [abs(x2 - x1) for x1, x2 in zip([x[1] for x in position], [x[1] for x in position][1:])]
                        # print("Khoảng cách giữa các phần tử liên tiếp:", x_distances1)
                        average_distance1 = sum(x_distances1) / len(x_distances1) if x_distances1 else 0
                        # print("Khoảng cách trung bình:", average_distance1)
                        greater_than_avg1 = [(i, d) for i, d in enumerate(x_distances1) if d > average_distance1+80]
                        # print("greater_than_avg1: ", greater_than_avg1)
                        # Tạo danh sách mới, chỉ giữ các khoảng cách không vượt quá (average_distance + 40)
                        filtered_distance1 = [d for d in x_distances1 if d <= average_distance1 + 80]
                        new_average_distance1 = sum(filtered_distance1) / len(filtered_distance1) if filtered_distance1 else 0
                        if len(greater_than_avg1) >= 1:
                            for i, d in greater_than_avg1:
                                # print(f"Khoảng cách lớn hơn trung bình tại vị trí {i+1}: {d}")
                                x_new = position[i][1] + new_average_distance1
                                # cv2.circle(img, (int(x_new), int(y_avg1)), 1, (255, 100, 255), 3)
                                distance_new2 = sqrt((int(x_new))**2 + (int(y_avg1)**2))
                                # Thêm vào danh sách và sắp xếp
                                position.append((distance_new2, int(x_new), int(y_avg1)))
                                # position.sort()
                                distance_tuples.append((distance_new2, int(x_new), int(y_avg1)))
                                # print("position: ", position)
                            if len(greater_than_avg1) == 1:
                                position.clear()  # Chỉ xóa position nếu có đúng 1 phần tử
                            count = 0
                            position.clear()
                        elif len(x_distances1) != 9: 
                            # print("Tô ở vị trí cuối cùng")
                            x_last = position[-1][1]+average_distance1
                            # cv2.circle(img, (int(x_last), int(y_avg1)), 1, (255, 100, 255), 3)
                            distance_new2 = sqrt((int(x_last))**2 + (int(y_avg1)**2))
                            position.append((distance_new2, int(x_last), int(y_avg1)))
                            distance_tuples.append((distance_new2, int(x_last), int(y_avg1)))
                            count = 0
                            position.clear()
                            position.sort()
                k+=1        
                # print("len of position: ", len(position))
                for distance, x, y in position:
                    col.append((x))
                    row.append((y))
                position.clear()
        for m in range(len(col)):
            if m % 10 == 9 and m < 100:
                if col[m] > max_x:
                    new_index = m - 9  # vị trí đầu của mỗi cột logic
                    a = row[m-8]
                    # print("m: ", m)
                    # print("a: ", a)
                    # Dồn các phần tử trong "cột logic" này từ new_index đến m-1 sang phải 1 vị trí
                    for i in range(m - 1, new_index - 1, -1):
                        col[i + 1] = col[i]
                        row[i + 1] = row[i]
                    # Gán giá trị mới vào đầu cột
                    col[new_index] = min_x  
                    row[new_index] = a
        self.col_save = col
        self.row_save = row

        if self.initial.CameraConnected and self.initial.PLCConnected:
            self.image_paths = [
                os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory)
                if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))
            ]
            self.bbox1 = []
            for m in range(len(self.col_save)):
                x1 = self.col_save[m] - bbox_width // 2
                y1 = self.row_save[m] - bbox_height // 2
                x2 = self.col_save[m] + bbox_width // 2
                y2 = self.row_save[m] + bbox_height // 2
                self.bbox1.append((x1, y1, x2, y2))
            
            if self.image_paths:
                print("There are images in the image_paths list.")
                for image_path in self.image_paths:
                    results = run_inference(
                        self.model, self.device, self.half, self.stride, self.imgsz, image_path, self.opt
                    )
                    print("Length of results:", len(results))
                    if results == []:
                        print("No results found.")
                        os.remove(image_path)
                    else:
                        for (class_name, confidence), pos, filename in results:
                            self.prediction = True
                            self.result.append((filename, pos))
                            # cv2.rectangle(self.img, (pos[0], pos[1]), (pos[2], pos[3]), (150, 255, 120), 2)
                            if class_name == "rubbertrays":
                                files = os.listdir(self.image_output)
                                if files:
                                    file_path = os.path.join(self.image_output, files[0])  # Lấy tệp đầu tiên
                                    os.remove(file_path)  # Xóa tệp
                                    print(f"Đã xóa tệp: {file_path}")
                if self.prediction:
                    self.task1_worker = Task1Worker(self.img,self.main,self.paraconfirm,self.col_save,self.row_save,self.detected_circles_model)  
                    if self.task1_worker.finished.connect(self.onTask1Finished):
                        print("Signal connected successfully!")
                    else:
                        print("Signal connection failed.")
                    try:
                        self.task1_worker.start()
                    except Exception as e:
                        print("Error when starting task1_worker:", e)
                    if "PLASTIC" in self.main.label_56.text():
                        self.task2_worker = Task2Worker(self.dashboard,self.result, self.paraconfirm, self.main)
                        self.task2_worker.bad.connect(self.onTask2Bad) 
                        self.task2_worker.good.connect(self.onTask2Good)
                        self.task2_worker.time.connect(self.onTask2Time)
                        self.task2_worker.pos1.connect(self.onTask2Pos1)
                        self.task2_worker.pos2.connect(self.onTask2Pos2)
                        self.task2_worker.finished1.connect(self.onTask2Finish)
                        self.task2_worker.start()
                    # else: 
                    #     self.task1_worker.finished.connect(self.onTaskRubberFinish)

    def onTask1Finished(self, pipes_count_model, rectangles_to_remove, pixmap, time_elapsed):
        self.Shortage_Time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        if pipes_count_model != 100:
            self.warning_alert()

        print(f"Task 1 finished. Pipes: {pipes_count_model}, Missing: {len(rectangles_to_remove)}")
        self.main.lbGeneralImage.setPixmap(pixmap)
        self.main.lbShortagetubes.setText(str(len(rectangles_to_remove)))
        self.dashboard.Total += 100
        self.main.lbTotal.setText(str(self.dashboard.Total))
        #Hiển thị miliseconds
        self.main.lbTimeCounter.setText(str(round(time_elapsed*1000, 2)))
        # Tạo danh sách các bước cần thực hiện
        self.update_steps = [
            (i, (i - 1) in rectangles_to_remove) for i in range(1, 101)
        ]
        self.update_steps.reverse()  # Đảo ngược danh sách để cập nhật từ 100 đến 1
        self.update_rubber_steps = [
            (i, (i - 1) not in rectangles_to_remove) for i in range(1, 101)
        ]
        self.update_rubber_steps.reverse()  # Đảo ngược danh sách để cập nhật từ 100 đến 1
        self.update_step_index = 0
        self.update_rubber_step_index = 0
        # Kích hoạt cập nhật UI liên tục mà không chặn luồng chính
        self.update_ui_step()
        for i in range(0, 100):
            if i in rectangles_to_remove:
                self.shortage_pos.append(i)
        
    def update_ui_step(self):
        text_label = self.main.label_56.text()
        is_rubber = "RUBBER" in text_label  # Kiểm tra nếu có chữ "RUBBER"

        # Duyệt qua toàn bộ update_steps
        for i, is_missing in self.update_steps:
            rotated_pos = 101 - i
            label_name = f"lbPos{rotated_pos}"
            if is_missing:
                color = "#FFDE21"  # Tô màu vàng
                self.dashboard.SetStyleSheetLable(label_name, color)

        # Nếu có RUBBER, xử lý thêm danh sách rubber
        if is_rubber:
            for j, is_existing in self.update_rubber_steps:
                rotated_pos_rubber = 101 - j
                label_name_rubber = f"lbPos{rotated_pos_rubber}"
                if is_existing:
                    color = "#33D909"  # Tô màu xanh lá cây
                    self.dashboard.SetStyleSheetLable(label_name_rubber, color)    
    
    def onTask2Bad(self, bad_count, pixmap):
        self.main.lbDefectiveImage.setPixmap(pixmap)
        self.main.lbDefectivetubes.setText(str(bad_count))
        if self.main.lbDefectivetubes.text() != "0":
            self.warning_alert()

    def onTask2Good(self, pixmap):
        self.main.lbDefectiveImage.setPixmap(pixmap)
        #Hiển thị miliseconds
    def onTask2Time(self, time_elapsed):
        #Hiển thị miliseconds
        self.main.lbTimeDetect.setText(str(round(time_elapsed, 3)))

    def onTask2Pos1(self, pos):
        # Lấy bbox2 từ pos
        x1, y1, x2, y2 = pos[0], pos[1], pos[2], pos[3]
        bbox2 = (x1, y1, x2, y2)
        max_iou = 0  # Biến lưu IoU lớn nhất
        best_bbox = None  # Lưu bbox có IoU lớn nhất
        # Duyệt qua từng bbox trong self.bbox1
        for bbox1 in self.bbox1:
            # Tính tọa độ phần giao nhau
            x1_inter = max(bbox1[0], bbox2[0])
            y1_inter = max(bbox1[1], bbox2[1])
            x2_inter = min(bbox1[2], bbox2[2])
            y2_inter = min(bbox1[3], bbox2[3])
            # Tính diện tích phần giao nhau
            inter_width = max(0, x2_inter - x1_inter)
            inter_height = max(0, y2_inter - y1_inter)
            inter_area = inter_width * inter_height
            # Tính diện tích từng box
            box1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
            box2_area = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
            # Tính IoU
            iou = inter_area / float(box1_area + box2_area - inter_area)
            # Cập nhật max IoU
            if iou > max_iou:
                max_iou = iou
                best_bbox = bbox1

        if best_bbox:
            best_pos = self.bbox1.index(best_bbox) + 1
            rotated_pos = 101 - best_pos
            self.bad_pos.append(rotated_pos)
            print("Bad position arr:", self.bad_pos)
            # Đổi màu thành #F23030 cho vị trí lớn nhất
            label_name = f"lbPos{rotated_pos}"
            print("Bad position:", label_name)
            self.dashboard.SetStyleSheetLable(label_name, "#F23030")

    def onTask2Pos2(self, pos):
        # Lấy bbox2 từ pos
        x1, y1, x2, y2 = pos[0], pos[1], pos[2], pos[3]
        bbox2 = (x1, y1, x2, y2)
        max_iou = 0  # Biến lưu IoU lớn nhất
        best_bbox = None  # Lưu bbox có IoU lớn nhất
        # Duyệt qua từng bbox trong self.bbox1
        for bbox1 in self.bbox1:
            # Tính tọa độ phần giao nhau
            x1_inter = max(bbox1[0], bbox2[0])
            y1_inter = max(bbox1[1], bbox2[1])
            x2_inter = min(bbox1[2], bbox2[2])
            y2_inter = min(bbox1[3], bbox2[3])
            # Tính diện tích phần giao nhau
            inter_width = max(0, x2_inter - x1_inter)
            inter_height = max(0, y2_inter - y1_inter)
            inter_area = inter_width * inter_height
            # Tính diện tích từng box
            box1_area = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
            box2_area = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
            # Tính IoU
            iou = inter_area / float(box1_area + box2_area - inter_area)
            # Cập nhật max IoU
            if iou > max_iou:
                max_iou = iou
                best_bbox = bbox1
        if best_bbox:
            best_pos = self.bbox1.index(best_bbox) + 1
            # Đổi màu thành #33D909 cho vị trí lớn nhất
            rotated_pos = 101 - best_pos
            label_name = f"lbPos{rotated_pos}"
            # print("Good position:", label_name)
            self.dashboard.SetStyleSheetLable(label_name, "#33D909")

    def onTask2Finish(self, DefectiveTime):
        self.finished.emit(self.bad_pos, self.shortage_pos, DefectiveTime, self.Shortage_Time)
        if self.bad_pos is not None:
            self.bad_pos.clear()
        
    def onTaskRubberFinish(self):
        self.finished.emit([], self.shortage_pos, [], self.Shortage_Time)
        
    def warning_alert(self):
        self.main.btnReset.setEnabled(True)
        self.SetStyleSheetForbtn("btnReset", "#FFDE21")

    def SetStyleSheetForbtn(self, btn, background_color):
        #Style cho nút 
        button = getattr(self.main, btn)
        button.setStyleSheet(f"""
                QPushButton#{btn} {{
                    border-radius: 15px;
                    border-color: white;
                    background-color: {background_color};  /* Màu nền mới */
                    color: white;
                    text-align: center;
                    font-family: Inter, sans-serif;
                }}

                QPushButton#{btn}:hover {{
                    background-color: #FFA500;  /* Màu nền khi hover */
                }}

                QPushButton#{btn}:pressed {{
                    padding-left: 5px;
                    padding-top: 5px;
                }}
                """)
