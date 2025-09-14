from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage, QPixmap, QTransform
import cv2
import numpy as np
from math import sqrt
import time



class Task1Worker(QThread):
    finished = pyqtSignal(int, list, object, float)  # Truyền số lượng ống và vị trí bị thiếu

    def __init__(self, img, main, paraconfirm, col, row, detected_circles_model):
        super().__init__()
        self.img = img
        self.main = main
        self.paraconfirm = paraconfirm
        self.roi = None
        self.hsv_roi = None
        self.col_save = col
        self.row_save = row
        self.detected_circles_model = detected_circles_model
    
    def run(self):
        print("Starting task 1...")
        self.StartTime = time.time()
        
        pipes_count_model = 0
        bbox_width = 125
        bbox_height = 125
        #Biến để thực hiện thuật toán sắp xếp vị trí các ống
        pos_count = 0
        # x_arr = []
        # y_arr = []
        # y_search = 0
        # distance_tuples = []
        # distance_tuples1 = []
        # row = []
        # col = []
        #Biến để nhận diện chấm màu đỏ
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([179, 255, 255])
        #Mảng lưu các vị trí bị mất của các ống (nếu có)
        rectangles_to_remove = []
        detected_circles = self.process_detected_circles(self.detected_circles_model)
        pipes_count_model = len(detected_circles)
        for points in detected_circles:
            a, b, r = points[0], points[1], points[2]
            cv2.circle(self.img, (a, b), 30, (0, 0, 255), 5)

        for m in range(len(self.col_save)):
            pos_count+=1
            top_left = (self.col_save[m] - bbox_width // 2, self.row_save[m] - bbox_height // 2)
            bottom_right = (self.col_save[m] + bbox_width // 2, self.row_save[m] + bbox_height // 2)
            # cv2.rectangle(self.img, top_left, bottom_right, (0, 255, 0), 2)
            self.roi = self.img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            self.hsv_roi = cv2.cvtColor(self.roi, cv2.COLOR_BGR2HSV)
            mask1 = cv2.inRange(self.hsv_roi, lower_red1, upper_red1)
            mask2 = cv2.inRange(self.hsv_roi, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(mask1, mask2)
            if not np.any(red_mask):
                rectangles_to_remove.append(m)

        frame = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(850, 445, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        #Xoay 180 độ ảnh 
        scaled_pixmap = scaled_pixmap.transformed(QTransform().rotate(180))

        print(pipes_count_model)
        print(rectangles_to_remove)
        try:
            execution_time = time.time() - self.StartTime
            self.finished.emit(pipes_count_model, rectangles_to_remove, scaled_pixmap,execution_time)
        except Exception as e:
            print("Error when emitting signal:", e)

    def process_detected_circles(self,detected_circles_model):
        if detected_circles_model is not None:
            detected_circles = np.uint16(np.around(detected_circles_model))
            detected_circles = sorted(detected_circles[0, :], key=lambda x: (x[0], x[1]))
            return detected_circles
        return []