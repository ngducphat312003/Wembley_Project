from MainUI1 import Ui_MainWindow
from PyQt6.QtWidgets import QTableWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt, QDateTime
from page_Initial import PageInitialBackend
from page_Parameter import PageParameterBackend
from pymelsec.constants import DT
import cv2
import time
from PyQt6.QtGui import QPixmap, QImage, QTransform
import os
import numpy as np
import torch
from CubeDetection import load_model, run_inference
from torchvision.models import mobilenet_v3_large
from torchvision.transforms import transforms
from pathlib import Path
import subprocess
import shutil
from PIL import Image
from sklearn.decomposition import PCA
import joblib
import re
from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix, f1_score
import matplotlib.pyplot as plt
from worker import Worker 
####################################################################################
class ConfigurationBackend():
    def __init__(self, main: Ui_MainWindow, conn, KeyPrimary, para: PageParameterBackend, initial: PageInitialBackend):
        self.parent = main
        self.conn = conn
        self.KeyPrimary = KeyPrimary
        self.para = para
        self.initial = initial
        #Chạy thực tế
        # self.trigger = PageInitialBackend.Camera.f.TriggerSoftware  # Initialize trigger to None
        self.delay = 0
        self.image_directory = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceImages1"
        self.output_folder = Path(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult")
        self.default_directory = r"H:\APP UNIVERSITY\CODE PYTHON\DatasetForTrainning"
        self.model_path = r"H:\APP UNIVERSITY\CODE PYTHON\ModelSaved"
        self.sorted_directory = None
        self.processing = False  # Trạng thái xử lý hình ảnh
        self.last_trigger_state = 0
        self.triggered = None
        self.Time_Start = None
        self.frame = None
        self.storage_feature = []
        self.storage_feature_pca = []
        self.pca = None
        self.storage_feature_final = []
        self.transform = None
        self.backbone = None
        self.best_threshold = None
        self.image_list = []
        self.heatmap_list = []
        self.current_index = -1 
        self.train_thread = None

        #Chạy thực tế
        # self.TriggerTimerConfirm = QTimer()
        # self.TriggerTimerConfirm.timeout.connect(self.TriggerImage)
        
        self.parent.stackedWidget_2.setCurrentWidget(self.parent.pageProductList)
        #PageProductList
        self.parent.btnAddData1.clicked.connect(lambda: [self.AddData1(), self.Push_working_history("Thêm sản phẩm mới")])
        #PageCollectingImage
        self.parent.btnReturn2_3.clicked.connect(lambda: [self.Return1(), self.Push_working_history("Quay lại danh sách sản phẩm")])
        self.parent.btnParameterConfirmation1_2.clicked.connect(lambda: [self.ConfirmData(), self.Push_working_history("Xác nhận tập dữ liệu cho sản phẩm mới")])
        #PageCounter
        self.parent.btnReturn2_2.clicked.connect(lambda: [self.Return2(), self.Push_working_history("Quay lại trang lấy dữ liệu")])
        self.parent.btnParemeterConfirm.clicked.connect(lambda: [self.ConfirmParameter(), self.Push_working_history("Xác nhận thông số HoughTransform cho sản phẩm mới")])
        #PageDefective
        self.parent.btnReturn2.clicked.connect(self.Return3)
        #Backend
        ###PageProductList
        self.SetupStyleTable(self.parent.tbProductList)
        #Hiển thị danh sách sản phẩm hiện có
        self.ShowProductList()
        ###PageCollectingImage
        #Hiển thị tên người thiết lập 
        self.parent.lbFullNameConfig_6.setText(self.parent.label_3.text())
        self.parent.lbDutyConfig_5.setText(self.parent.label_5.text())
        
        self.parent.leditProductName_8.setEnabled(False)
        self.parent.btnConfirmProduct.setEnabled(False)
        self.SetStyleSheetForbtn("btnConfirmProduct", "#A4A4A4")
        #Cho phép người dùng nhập tên sản phẩm
        self.parent.btnProductCreation_2.clicked.connect(lambda: [self.EnabledEditProductName(), self.Push_working_history("Thêm tên sản phẩm mới")])
        #Tạo sản phẩm mới và thêm vào cơ sở dữ liệu
        self.parent.btnModifyLight_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnModifyLight_2", "#A4A4A4")
        self.parent.btnSaveLight_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveLight_2", "#A4A4A4")
        self.parent.btnModifyCounter1_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnModifyCounter1_2", "#A4A4A4")
        self.parent.btnSaveCounter1_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCounter1_2", "#A4A4A4")
        self.parent.btnTry_3.setEnabled(False)
        self.SetStyleSheetForbtn("btnTry_3", "#A4A4A4")
        self.parent.btnTry_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnTry_2", "#A4A4A4")
        #Chạy thực tế
        # self.parent.btnParameterConfirmation1_2.setEnabled(False)
        # self.SetStyleSheetForbtn("btnParameterConfirmation1_2", "#A4A4A4")
        self.parent.btnConfirmProduct.clicked.connect(lambda: [self.CreateProduct(), self.Push_working_history("Xác nhận tên sản phẩm mới")])
        #Nút điều chỉnh thông số đèn
        self.parent.leditLight1_2.setEnabled(False)
        self.parent.leditLight2_2.setEnabled(False)
        self.parent.leditLight3_2.setEnabled(False)
        self.parent.leditLight4_2.setEnabled(False)
        self.parent.btnModifyLight_2.clicked.connect(lambda: [self.ModifyLight(), self.Push_working_history("Điều chỉnh thông số đèn cho sản phẩm mới")])
        #Nút lưu thông số đèn
        self.parent.btnSaveLight_2.clicked.connect(lambda: [self.SaveLight(), self.Push_working_history("Lưu thông số đèn cho sản phẩm mới")])
        #Nút điều chỉnh thông số delay
        self.parent.leditTriggerDelay_3.setEnabled(False)
        self.parent.btnModifyCounter1_2.clicked.connect(lambda: [self.ModifyDelay(), self.Push_working_history("Điều chỉnh thông số delay cho sản phẩm mới")])
        #Nút lưu thông số delay
        self.parent.btnSaveCounter1_2.clicked.connect(lambda: [self.SaveDelay(), self.Push_working_history("Lưu thông số delay cho sản phẩm mới")])
        #Chạy thực tế
        # self.TriggerCounterImage = QTimer()
        # self.TriggerCounterImage.timeout.connect(self.CountImage)
        # self.TriggerCounterImage.start(500)
        #Đếm số lượng mẫu test
        self.parent.lbTestCounter_2.setText("0")
        self.ImageCounter = 1
        self.parent.btnTry_3.clicked.connect(lambda: [self.ConfirmProduct(), self.Push_working_history("Xác nhận hình ảnh cho tập dữ liệu mới")])   
        self.parent.btnTry_2.clicked.connect(lambda: [self.StartTrigger(), self.parent.lbImageConfirm_2.clear(), self.parent.btnTry_2.setEnabled(False), self.SetStyleSheetForbtn("btnTry_2", "#A4A4A4"), self.parent.btnTry_3.setEnabled(False), self.SetStyleSheetForbtn("btnTry_3", "#A4A4A4"), self.Push_working_history("Tiếp tục lấy hình ảnh cho tập dữ liệu mới")])

        ###PageCounter
        self.parent.lbFullNameConfig_5.setText(self.parent.lbFullNameConfig_6.text())
        self.parent.lbDutyConfig_4.setText(self.parent.lbDutyConfig_5.text())
        self.parent.btnTest.setEnabled(False)
        self.SetStyleSheetForbtn("btnTest", "#A4A4A4")
        self.parent.btnSaveConfig.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveConfig", "#A4A4A4")
        self.parent.btnParemeterConfirm.setEnabled(False)
        self.SetStyleSheetForbtn("btnParemeterConfirm", "#A4A4A4")
        #Cho phép điều chỉnh thông số HoughTransform
        self.parent.btnModifyConfig.clicked.connect(lambda: [self.EnabledEditPara(), self.Push_working_history("Điều chỉnh thông số HoughTransform cho sản phẩm mới")])
        #Kiểm tra thông số HoughTransform
        self.parent.btnTest.clicked.connect(lambda: [self.TestHoughTransform(), self.Push_working_history("Kiểm tra thông số HoughTransform")])
        #Lưu thông số HoughTransform
        self.parent.btnSaveConfig.clicked.connect(lambda: [self.SavePara(), self.Push_working_history("Lưu thông số HoughTransform cho sản phẩm mới")])

        ###PageDefective
        self.parent.lbFullNameConfig_3.setText(self.parent.lbFullNameConfig_5.text())
        self.parent.lbDutyConfig_2.setText(self.parent.lbDutyConfig_4.text())
        self.parent.btnDataCollecting.setEnabled(False)
        self.SetStyleSheetForbtn("btnDataCollecting", "#A4A4A4")
        self.parent.btnSaveData.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveData", "#A4A4A4")
        self.parent.btnTraningModel.setEnabled(False)
        self.SetStyleSheetForbtn("btnTraningModel", "#A4A4A4")
        self.parent.btnConfirmModel.setEnabled(False)
        self.SetStyleSheetForbtn("btnConfirmModel", "#A4A4A4")
        self.parent.btnResultScreening.setEnabled(False)
        self.SetStyleSheetForbtn("btnResultScreening", "#A4A4A4")
        #Thực hiện tiền xử lí dữ liệu
        self.parent.btnDataCollectingStop.clicked.connect(lambda: [self.DataPreprocessing(), self.Push_working_history("Tiền xử lý dữ liệu")])
        #Sắp xếp dữ liệu
        self.parent.btnModifyData.setEnabled(False)
        self.SetStyleSheetForbtn("btnModifyData", "#A4A4A4")
        self.parent.btnDataCollecting.clicked.connect(lambda: [self.DataSorting(), self.Push_working_history("Sắp xếp dữ liệu cho sản phẩm mới")])
        #Thêm dữ liệu vào thư mục cố định
        self.parent.btnAddData.clicked.connect(lambda: [self.AddDataset(), self.Push_working_history("Thêm dữ liệu vào thư mục cố định")])
        #Cập nhật dữ liệu dữ liệu huấn luyện
        self.parent.btnModifyData.clicked.connect(lambda: [self.UpdateDataset(), self.Push_working_history("Cập nhật dữ liệu huấn luyện")])
        #Xác nhận dữ liệu huấn luyện
        self.parent.leditSizeEstablish.setEnabled(False)
        self.parent.btnEstablish.setEnabled(False)
        self.SetStyleSheetForbtn("btnEstablish", "#A4A4A4")
        self.parent.btnSaveData.clicked.connect(lambda: [self.ConfirmDataset(), self.Push_working_history("Xác nhận dữ liệu huấn luyện")])
        #Thiết lập số lượng training
        self.parent.btnEstablish.clicked.connect(lambda: [self.EstablishTraining(), self.Push_working_history("Thiết lập số lượng training")])
        #Huấn luyện mô hình
        self.parent.btnTraningModel.clicked.connect(lambda: [self.TrainingModel(), self.Push_working_history("Huấn luyện mô hình")])
        #Xác nhận mô hình
        self.parent.btnConfirmModel.clicked.connect(lambda: [self.ConfirmModel(), self.Push_working_history("Lưu mô hình")])
        #Xem kết quả huấn luyện
        self.parent.btnResultScreening.clicked.connect(lambda: [self.on_result_screening(), self.Push_working_history("Xem hình ảnh kết quả huấn luyện")])
        #Nút đi lên 
        self.parent.btnUp.clicked.connect(self.on_previous_button)
        #Nút đi xuống
        self.parent.btnDown.clicked.connect(self.on_next_button)
        #Huấn luyện lại mô hình
        self.parent.btnTryingTrain.clicked.connect(lambda: [self.TryTrainingModel(), self.Push_working_history("Huấn luyện lại mô hình")])
        
    #Set style cho lable    
    def SetStyleSheetLable(self, object, background_color):
        #Style cho nút btnEmployeeWorking
        button = getattr(self.parent, object)
        button.setStyleSheet(f"""
                QLabel#{object} {{
                    border-radius: 15px;
                    border-color: 1px solid #FFFFFF;
                    background-color: {background_color};  /* Màu nền mới */
                    color: white;
                    text-align: center;
                    font-family: Inter, sans-serif;
                }}""")  
    #Set style cho nút
    def SetStyleSheetForbtn(self, btn, background_color):
        #Style cho nút 
        button = getattr(self.parent, btn)
        button.setStyleSheet(f"""
                QPushButton#{btn} {{
                    border-radius: 20px;
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
    
    def AddData1(self):
        print("AddData1")
        self.parent.stackedWidget_2.setCurrentWidget(self.parent.PageCollectingImage) 
    
    def Return1(self):
        print("Return1")
        self.parent.stackedWidget_2.setCurrentWidget(self.parent.pageProductList)
        self.ShowProductList()

    def ConfirmData(self):
        print("ConfirmData")
        self.parent.stackedWidget_2.setCurrentWidget(self.parent.pageCounter)
        #Kiểm tra số lượng file trong thư mục và đếm số lượng mẫu test
        self.ImageCounter1 = len([name for name in os.listdir(self.image_directory) if os.path.isfile(os.path.join(self.image_directory, name))])
        if self.ImageCounter1 == self.ImageCounter:
            print("Số lượng mẫu test đã đủ!")
        else:
            print("Số lượng mẫu test chưa đủ!")
            self.parent.lbTestCounter_2.setText(str(self.ImageCounter1))
            self.parent.btnTry_3.setEnabled(True)
            self.SetStyleSheetForbtn("btnTry_3", "#0055FF")
            self.parent.btnTry_2.setEnabled(True)
            self.SetStyleSheetForbtn("btnTry_2", "#0055FF")
        self.parent.lbTubeName_3.setText(self.parent.lbTubeName_4.text())    
        #Hiển thị hình ảnh từ self.image_directory
        self.ScreeningImage()
            
    def Return2(self):
        print("Return2")
        self.parent.stackedWidget_2.setCurrentWidget(self.parent.PageCollectingImage)

    def ConfirmParameter(self):
        print("ConfirmParameter")
        self.parent.stackedWidget_2.setCurrentWidget(self.parent.pageDefective)
        self.parent.lbTubeName_2.setText(self.parent.lbTubeName_3.text())
    
    def Return3(self):
        print("Return3")
        self.parent.stackedWidget_2.setCurrentWidget(self.parent.pageProductList)
        self.ShowProductList()

    def EnabledEditProductName(self):
        self.parent.leditProductName_8.setEnabled(True)
        self.parent.btnConfirmProduct.setEnabled(True)
        self.SetStyleSheetForbtn("btnConfirmProduct", "#0055FF")
        #Cập nhật tên filename vào cơ sở dữ liệu
        c = self.conn.cursor()
        match = re.match(r"([A-Z]+)PLASTIC", self.parent.lbTubeName_4.text())
        print("match:",match)
        if match:
            color = match.group(1).lower()
            print("color:", color)
        # self.cursor.execute("UPDATE Product SET FileName = ? WHERE ProductName = ?",
        #                     (match, self.parent.lbTubeName_4.text()))        

    def CreateProduct(self):
        self.parent.btnModifyLight_2.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyLight_2", "#33D909")
        self.parent.btnModifyCounter1_2.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyCounter1_2", "#33D909")
        product_name = self.parent.leditProductName_8.text()
        if not product_name:
            print("Vui lòng nhập tên sản phẩm.")
            return
        #Thêm sản phẩm vào cơ sở dữ liệu
        self.cursor = self.conn.cursor()
        self.cursor.execute("INSERT INTO Product (ProductName) VALUES (?)", (product_name,))
        self.conn.commit()
        print(f"Sản phẩm '{product_name}' đã được thêm vào cơ sở dữ liệu.")
        #Hiển thị danh sách sản phẩm hiện có
        self.ShowProductList()
        #Đặt lại trạng thái của nút và ô nhập liệu
        self.parent.leditProductName_8.setEnabled(False)
        self.parent.btnConfirmProduct.setEnabled(False)
        self.SetStyleSheetForbtn("btnConfirmProduct", "#A4A4A4")
        self.parent.btnProductCreation_2.setEnabled(True)
        self.SetStyleSheetForbtn("btnProductCreation_2", "#33D909")
        self.parent.leditProductName_8.clear()  # Xóa ô nhập liệu
        self.parent.lbTubeName_4.setText(product_name)  # Cập nhật tên sản phẩm trên giao diện

    def ModifyLight(self):
        self.parent.leditLight1_2.setEnabled(True)
        self.parent.leditLight2_2.setEnabled(True)
        self.parent.leditLight3_2.setEnabled(True)
        self.parent.leditLight4_2.setEnabled(True)
        self.parent.btnSaveLight_2.setEnabled(True)
        self.SetStyleSheetForbtn("btnSaveLight_2", "#DF2026")
        self.parent.btnModifyLight_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnModifyLight_2", "#A4A4A4")
    # Lấy biến PLC để kích hoạt camera trigger
    def GetPlcVariableForTrigger(self):
        if PageInitialBackend.PLCConnected == True and PageInitialBackend.CameraConnected == True:
            for i in range(self.initial.dinput_lenght):
                try:
                    # Đọc biến từ PLC
                    read_result = self.initial.Plc.batch_read(ref_device='X0', read_size=30, data_type=DT.BIT)
                    RealValue1 = int(read_result[29].value)
                    
                    if self.initial.dinput_old[20] != RealValue1:
                        # self.TriggerTimerConfirm.stop()
                        self.initial.dinput_old[20] = RealValue1
                        print("S3/in/19", RealValue1)
                            
                    trigger_value = RealValue1
                    # Break the loop or return from the function to stop the trigger
                    if trigger_value == 1  and self.last_trigger_state == 0:  
                        self.triggered = True  # Đặt cờ sự kiện kích hoạt
                        self.processing = True
                    elif trigger_value == 0:
                        self.processing = False  # Reset lại trạng thái xử lý khi trigger_value là 0
                    self.last_trigger_state = trigger_value  # Cập nhật trạng thái trước của trigger_value
                    return
                except Exception as e:
                    print("Failed to get PLC variable:", e)
                    self.triggered = False  # Đặt lại cờ sự kiện kích hoạt nếu có lỗi
    #Xử lí hình ảnh thông qua cảm biến trigger
    def TriggerImage(self):
        #Lấy thông số delay từ database
        if PageInitialBackend.PLCConnected == True and PageInitialBackend.CameraConnected == True:
            self.GetPlcVariableForTrigger()
            #print("Waiting for next trigger")
            # print("Trigger state:", self.triggered)
            if self.triggered:
                self.processing = True
                print("Trigger activated, processing images...")
                try:
                    #start = time.time()
                    print("Delay:", self.delay)
                    time.sleep(self.delay)
                    if self.trigger:
                        self.trigger.Execute()
                    else:
                        print("Trigger is not initialized.")
                    self.img_camera = self.initial.Camera.GetImage()
                    # file_path = self.GetNextFilename()
                    # self.img_camera.Save(file_path)
                    if self.img_camera is None:
                        print("Không thể lấy ảnh từ camera!")
                    else:
                        print("Ảnh đã được lấy thành công!")
                    #Hiển thị hình ảnh
                    frame = self.img_camera.GetNPArray()
                    if frame is None or frame.size == 0:
                        print("Ảnh nhận được trống! Bỏ qua frame này.")
                    else:
                        print("Ảnh nhận được không trống! Hiển thị ảnh...")
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    height, width, channel = frame.shape
                    x1 = int(width * 0.12)
                    x2 = int(width * 0.79)
                    y_start = int(height * 0.1)
                    y_end = int(height * 0.9)
                    line_color = (0, 255, 0)  # Màu xanh lá (R, G, B)
                    line_thickness = 2  
                    cv2.line(frame, (x1, y_start), (x1, y_end), line_color, line_thickness)
                    cv2.line(frame, (x2, y_start), (x2, y_end), line_color, line_thickness)
                    bytes_per_line = 3 * width
                    q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_image)
                    scaled_pixmap = pixmap.scaled(800, 565, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.parent.lbImageConfirm.setPixmap(scaled_pixmap)
                    #Thực tế
                    #self.CountImage()
                    self.triggered = False  # Đặt lại trigger để chờ lần kích hoạt tiếp theo
                    self.processing = False  
                except Exception as e:
                    print(f"Error capturing or saving image: {e}")
                    self.triggered = False
                finally:
                    # Reset trigger sau khi hoàn thành xử lý
                    self.triggered = False
                    self.processing = False
    #Đếm số lần hiển thị hình ảnh
    def CountImage(self):
        #Kiểm tra lbImageConfirm có đang chứa hình ảnh không
        pixmap = self.parent.lbImageConfirm_2.pixmap()
        if pixmap and not pixmap.isNull():
            self.parent.btnTry_2.setEnabled(True)
            self.SetStyleSheetForbtn("btnTry_2", "#F68013")
            self.parent.btnTry_3.setEnabled(True)
            self.SetStyleSheetForbtn("btnTry_3", "#0055FF")
            self.TriggerTimerConfirm.stop()
            self.TriggerCounterImage.stop() 
        else:
            self.parent.btnTry.setEnabled(False)
            self.SetStyleSheetForbtn("btnTry_2", "#A4A4A4")
            self.TriggerTimerConfirm.start(10)
    # Khi nhấn nút btnTry_2 hoặc btnTry_3 và ImageCounter > 0        
    def StartTrigger(self):
        if self.ImageCounter > 0:
            self.TriggerTimerConfirm.start(10)  # Bắt đầu timer mỗi 500ms
            self.TriggerCounterImage.start(500)
            print("Trigger đang chạy...")

        else:
            print("Không thể chạy trigger, Test Counter = 0")

    def SaveLight(self):
        self.parent.btnSaveLight_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveLight_2", "#A4A4A4")
        self.parent.leditLight1_2.setEnabled(False)
        self.parent.leditLight2_2.setEnabled(False)
        self.parent.leditLight3_2.setEnabled(False)
        self.parent.leditLight4_2.setEnabled(False)
        self.parent.btnModifyLight_2.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyLight_2", "#33D909")
        #Lưu thông số đèn vào cơ sở dữ liệu
        light1 = float(self.parent.leditLight1_2.text())
        light2 = float(self.parent.leditLight2_2.text())
        light3 = float(self.parent.leditLight3_2.text())
        light4 = float(self.parent.leditLight4_2.text())
        if not light1 or not light2 or not light3 or not light4:
            print("Vui lòng nhập đầy đủ thông số đèn.")
            return
        #Thêm thông số đèn vào cơ sở dữ liệu
        self.cursor = self.conn.cursor()
        self.cursor.execute("UPDATE Product SET LIGHT1 = ?, LIGHT2 = ?, LIGHT3 = ?, LIGHT4 = ? WHERE ProductName = ?",
                            (light1, light2, light3, light4, self.parent.lbTubeName_4.text()))
        self.conn.commit()

    def ModifyDelay(self):
        self.parent.leditTriggerDelay_3.setEnabled(True)
        self.parent.btnSaveCounter1_2.setEnabled(True)
        self.SetStyleSheetForbtn("btnSaveCounter1_2", "#DF2026")
        self.parent.btnModifyCounter1_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnModifyCounter1_2", "#A4A4A4")

    def SaveDelay(self):
        self.parent.btnSaveCounter1_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCounter1_2", "#A4A4A4")
        self.parent.leditTriggerDelay_3.setEnabled(False)
        self.parent.btnModifyCounter1_2.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyCounter1_2", "#33D909")
        #Lưu thông số delay vào cơ sở dữ liệu
        self.delay = float(self.parent.leditTriggerDelay_3.text())
        exposure_time = 1000
        width = 2592
        height = 2048
        offset_x = 0
        offset_y = 0
        print(self.delay)
        if not self.delay:
            print("Vui lòng nhập đầy đủ thông số delay.")
            return
        #Thêm thông số delay vào cơ sở dữ liệu
        self.cursor = self.conn.cursor()
        self.cursor.execute("UPDATE Product SET TriggerDelay = ?, ExposureTime = ?, Width = ?, Height = ?, OffsetX = ?, OffsetY = ? WHERE ProductName = ?",
                            (self.delay, exposure_time, width, height, offset_x, offset_y, self.parent.lbTubeName_4.text()))
        self.conn.commit()
        #Chạy trigger - thực tế
        # self.TriggerTimerConfirm.start(10) 
        # self.para.SetupCameraForTrigger()

    def ConfirmProduct(self):
        self.ImageCounter += 1
        self.parent.btnParameterConfirmation1_2.setEnabled(True)
        self.SetStyleSheetForbtn("btnParameterConfirmation1_2", "#33D909")
        self.parent.lbTestCounter_2.setText(str(self.ImageCounter))
        self.parent.btnTry_3.setEnabled(False)
        self.SetStyleSheetForbtn("btnTry_3", "#A4A4A4")
        self.parent.btnTry_2.setEnabled(False)
        self.SetStyleSheetForbtn("btnTry_2", "#A4A4A4")
        # self.StartTrigger()
        # self.parent.lbImageConfirm_2.clear()

    def EnabledEditPara(self):
        self.parent.btnTest.setEnabled(True)
        self.SetStyleSheetForbtn("btnTest", "#33D909")
        self.parent.leditProductName_2.setEnabled(True)
        self.parent.leditProductName_3.setEnabled(True)
        self.parent.leditProductName_4.setEnabled(True)
        self.parent.leditProductName_5.setEnabled(True)
        self.parent.leditProductName_6.setEnabled(True)
        self.parent.leditProductName_7.setEnabled(True)

        self.parent.leditProductName_2.setText("1.1")
        self.parent.leditProductName_3.setText("80")
        self.parent.leditProductName_4.setText("60")
        self.parent.leditProductName_5.setText("35")
        self.parent.leditProductName_6.setText("65")
        self.parent.leditProductName_7.setText("85")

        self.parent.btnModifyConfig.setEnabled(False)
        self.SetStyleSheetForbtn("btnModifyConfig", "#A4A4A4")

    def ScreeningImage(self):
        #Lấy file ảnh đầu tiên trong thư mục
        image_files = [f for f in os.listdir(self.image_directory) if f.endswith(('.jpg', '.png', '.bmp'))]
        if image_files:
            first_image_file = image_files[0]
            image_path = os.path.join(self.image_directory, first_image_file)
            #Đọc ảnh
            self.frame = cv2.imread(image_path)
            if self.frame is None:
                print("Không thể đọc ảnh từ file:", image_path)
                return
            #Chuyển đổi màu sắc từ BGR sang RGB
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            height, width, channel = self.frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(self.frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(800, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            scaled_pixmap = scaled_pixmap.transformed(QTransform().rotate(180))
            self.parent.lbCounterImage.setPixmap(scaled_pixmap)

    def TestHoughTransform(self):
        self.parent.btnSaveConfig.setEnabled(True)
        self.SetStyleSheetForbtn("btnSaveConfig", "#DF2026")
        #Lấy thông số HoughTransform từ các ô nhập liệu
        img = self.frame.copy()
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (5,5), 0)  
        self.detected_circles_model = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, dp=float(self.parent.leditProductName_2.text()), minDist=int(self.parent.leditProductName_3.text()),
                                 param1=int(self.parent.leditProductName_4.text()), param2=int(self.parent.leditProductName_5.text()), minRadius=int(self.parent.leditProductName_6.text()), maxRadius=int(self.parent.leditProductName_7.text()))
        detected_circles = self.process_detected_circles(self.detected_circles_model)
        pipes_count_model = len(detected_circles)
        print("Số lượng ống:", pipes_count_model)
        #Hiển thị số lượng kiểm tra
        self.parent.lbFullNameConfig_2.setText(str(pipes_count_model))
        for points in detected_circles:
            a, b, r = points[0], points[1], points[2]
            cv2.circle(img, (a, b), 2, (255, 0, 0), 3)
        #Hiển thị hình ảnh lên lbCounterImage
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(800, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        scaled_pixmap = scaled_pixmap.transformed(QTransform().rotate(180))
        self.parent.lbCounterImage.setPixmap(scaled_pixmap)

    def process_detected_circles(self, detected_circles_model):
        if detected_circles_model is not None:
            detected_circles = np.uint16(np.around(self.detected_circles_model))
            detected_circles = sorted(detected_circles[0, :], key=lambda x: (x[0], x[1]))
            return detected_circles
        return [] 

    def SavePara(self):
        #Lưu thông số HoughTransform vào cơ sở dữ liệu
        self.parent.btnSaveConfig.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveConfig", "#A4A4A4")
        self.parent.btnTest.setEnabled(False)
        self.SetStyleSheetForbtn("btnTest", "#A4A4A4")
        self.parent.leditProductName_2.setEnabled(False)
        self.parent.leditProductName_3.setEnabled(False)
        self.parent.leditProductName_4.setEnabled(False)
        self.parent.leditProductName_5.setEnabled(False)
        self.parent.leditProductName_6.setEnabled(False)
        self.parent.leditProductName_7.setEnabled(False)
        self.parent.btnModifyConfig.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyConfig", "#F68013")   
        #Lưu thông số HoughTransform vào cơ sở dữ liệu
        dp = float(self.parent.leditProductName_2.text())
        minDist = int(self.parent.leditProductName_3.text())
        param1 = int(self.parent.leditProductName_4.text())
        param2 = int(self.parent.leditProductName_5.text())
        minRadius = int(self.parent.leditProductName_6.text())
        maxRadius = int(self.parent.leditProductName_7.text())
        if not dp or not minDist or not param1 or not param2 or not minRadius or not maxRadius:
            print("Vui lòng nhập đầy đủ thông số HoughTransform.")
            return
        #Thêm thông số HoughTransform vào cơ sở dữ liệu
        self.cursor = self.conn.cursor()
        self.cursor.execute("UPDATE Product SET Dp = ?, minDist = ?, Param1 = ?, Param2 = ?, Minradius = ?, Maxradius = ? WHERE ProductName = ?",
                            (dp, minDist, param1, param2, minRadius, maxRadius, self.parent.lbTubeName_4.text()))
        self.conn.commit()
        self.parent.btnParemeterConfirm.setEnabled(True)
        self.SetStyleSheetForbtn("btnParemeterConfirm", "#33D909")

    def DataPreprocessing(self):
        classes_to_filter = None
        self.opt = {
            "weights": r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\yolov7.torchscript.pt",  # Path to weights file default weights are for nano model
            "img-size": 576,  # default image size
            "conf-thres": 0.5,  # confidence threshold for inference.
            "iou-thres": 0.45,  # NMS IoU threshold for inference.
            "device": '0' if torch.cuda.is_available() else 'cpu',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
            "classes": classes_to_filter  # list of classes to filter or None
        }
        self.model, self.device, self.half, self.stride, self.imgsz = load_model(self.opt)
        self.image_paths = [
                os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory)
                if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))
            ]
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
        for path in self.output_folder.glob('*.bmp'):
            file_path = str(path)
            img = cv2.imread(file_path)
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
            # ===== Lưu ảnh đã xử lý =====
            output_path = os.path.join(self.output_folder, os.path.basename(file_path))
            cv2.imwrite(output_path, img)
        self.parent.btnDataCollectingStop.setEnabled(False)
        self.SetStyleSheetForbtn("btnDataCollectingStop", "#A4A4A4")
        self.parent.btnDataCollecting.setEnabled(True)
        self.SetStyleSheetForbtn("btnDataCollecting", "#33D909")

    def DataSorting(self):
        #Tạo thư mục để lưu dữ liệu đã sắp xếp
        self.sorted_directory = os.path.join(r"H:\APP UNIVERSITY\CODE PYTHON", "Dataset_{0}".format(self.parent.lbTubeName_4.text()))
        os.makedirs(self.sorted_directory, exist_ok=True)
        #Kiểm tra đã có thư mục chưa
        if os.path.exists(self.sorted_directory):
            print("Thư mục đã tồn tại:", self.sorted_directory)
        #Tạo các thư mục con để lưu dữ liệu đã sắp xếp
        subdirectories = ['bl', 'br', 'mid', 'tl', 'tr']
        for subdir in subdirectories:
            subfolder_path = os.path.join(self.sorted_directory, subdir)  # Đường dẫn của thư mục con
            os.makedirs(subfolder_path, exist_ok=True)  # Tạo thư mục con nếu chưa có
            for category in ['train', 'test','eval']:
                category_path = os.path.join(subfolder_path, category)
                os.makedirs(category_path, exist_ok=True)
                # Tạo thư mục con 'good' trong thư mục 'train' và 'good'/'bad' trong thư mục 'test'
                if category == 'train':
                    good_path = os.path.join(category_path, 'good')
                    os.makedirs(good_path, exist_ok=True)
                elif category == 'test':
                    good_path = os.path.join(category_path, 'good')
                    bad_path = os.path.join(category_path, 'bad')
                    os.makedirs(good_path, exist_ok=True)
                    os.makedirs(bad_path, exist_ok=True)
        #Sắp xếp dữ liệu vào các thư mục con
        self.sorted_directory1 = Path(self.sorted_directory) 
        for image_path in self.output_folder.glob('*.bmp'):
            image_name = image_path.stem.lower()
            # Xác định thư mục đích dựa trên tên tệp
            if 'blplastic' in image_name:
                target_folder = self.sorted_directory1 / 'bl'
            elif 'brplastic' in image_name:
                target_folder = self.sorted_directory1 / 'br'
            elif 'midplastic' in image_name:
                target_folder = self.sorted_directory1 / 'mid'
            elif 'tlplastic' in image_name:
                target_folder = self.sorted_directory1 / 'tl'
            elif 'trplastic' in image_name:
                target_folder = self.sorted_directory1 / 'tr'
            else:
                continue  # Nếu tên tệp không khớp, bỏ qua tệp này
            # Tạo thư mục đích nếu chưa tồn tại
            target_folder.mkdir(parents=True, exist_ok=True)

            # Di chuyển tệp vào thư mục đích
            target_file_path = target_folder / image_path.name
            shutil.move(str(image_path), str(target_file_path))
        #Hiển thị thư mục đã tạo lên màn hình
        subprocess.run(f'explorer "{self.sorted_directory}"', shell=True)

    def AddDataset(self):
        self.parent.btnModifyData.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyData", "#F68013")
        subprocess.run(f'explorer "{self.sorted_directory}"', shell=True)
        subprocess.run(f'explorer "{self.default_directory}"', shell=True)
        
    def UpdateDataset(self):
        #Cập nhật số lượng dữ liệu trong thư mục
        self.parent.lbGoodTraining.setText(str(len(os.listdir(os.path.join(self.default_directory, 'train', 'good')))))
        self.parent.lbGoodTesting.setText(str(len(os.listdir(os.path.join(self.default_directory, 'test', 'good')))))
        self.parent.lbBadTesting.setText(str(len(os.listdir(os.path.join(self.default_directory, 'test', 'bad')))))
        self.parent.lbTrained.setText(str(len(os.listdir(os.path.join(self.default_directory, 'eval')))))
        self.parent.btnSaveData.setEnabled(True)
        self.SetStyleSheetForbtn("btnSaveData", "#DF2026")
        self.parent.btnModifyData.setEnabled(False)
        self.SetStyleSheetForbtn("btnModifyData", "#A4A4A4")

    def ConfirmDataset(self):
        #Kiểm tra số lượng dữ liệu trong thư mục khác 0
        if len(os.listdir(os.path.join(self.default_directory, 'train', 'good'))) == 0:
            print("Không có dữ liệu trong thư mục train/good")
            return
        if len(os.listdir(os.path.join(self.default_directory, 'test', 'good'))) == 0:
            print("Không có dữ liệu trong thư mục test/good")
            return
        if len(os.listdir(os.path.join(self.default_directory, 'test', 'bad'))) == 0:
            print("Không có dữ liệu trong thư mục test/bad")
            return
        if len(os.listdir(os.path.join(self.default_directory, 'eval'))) == 0:
            print("Không có dữ liệu trong thư mục eval")
            return
        
        self.parent.leditSizeEstablish.setEnabled(True)
        self.parent.leditSizeEstablish.setText("1.5")
        self.parent.btnEstablish.setEnabled(True)
        self.SetStyleSheetForbtn("btnEstablish", "#F68013")
        self.parent.btnSaveData.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveData", "#A4A4A4")

    def EstablishTraining(self):
        print("Setting up anomaly detection...")
        features = []
        self.storage_feature = []

        self.transform = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor()])
        class mobilenet_feature_extractor(torch.nn.Module):
            def __init__(self):
                super(mobilenet_feature_extractor, self).__init__()
            # Tải mô hình MobileNetV3 với trọng số đã huấn luyện
                self.model = mobilenet_v3_large(pretrained=True)

                # Đặt chế độ đánh giá và tắt gradient
                self.model.eval()
                for param in self.model.parameters():
                    param.requires_grad = False

                # Hook để trích xuất feature maps
                self.features = []
                def hook(module, input, output):
                    """Lưu lại các feature maps từ các tầng cụ thể."""
                    self.features.append(output)

                # Đăng ký hook vào các tầng mà bạn muốn trích xuất feature maps
                self.model.features[3].register_forward_hook(hook)  # Tầng giữa (middle layer)
                self.model.features[6].register_forward_hook(hook)  # Tầng sâu hơn (deeper layer)
                self.model.features[12].register_forward_hook(hook) # Một tầng sâu hơn nữa (deep layer)

            def forward(self, input):
                """Truyền đầu vào qua mô hình và thu thập feature maps."""
                self.features = []  # Để lưu các feature maps
                with torch.no_grad():
                    _ = self.model(input)  # Truyền qua mô hình

                # Feature maps từ các hook
                resized_maps = [
                    torch.nn.functional.adaptive_avg_pool2d(fmap, (28, 28)) for fmap in self.features
                ]
                patch = torch.cat(resized_maps, 1)  # Nối các feature maps
                patch = patch.reshape(patch.shape[1], -1).T  # Chuyển thành tensor dạng cột

                return patch
        self.backbone = mobilenet_feature_extractor().cuda()
        folder_path = Path(self.default_directory) / 'train' / 'good' 
        print("Folder path:", folder_path)
        position_keywords = {
            "blplastic": "bl",
            "brplastic": "br",
            "midplastic": "mid",
            "tlplastic": "tl",
            "trplastic": "tr"
        }
        for pth in folder_path.glob('*.bmp'):
            file_name = pth.stem.lower()
            for keyword, position in position_keywords.items():
                if keyword in file_name:
                    self.position_name = position
                    break
        for pth in folder_path.glob('*.bmp'):        
            with torch.no_grad():
                img = cv2.imread(pth)
                pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                data = self.transform(pil_image).cuda().unsqueeze(0)
                features = self.backbone(data)
                self.storage_feature.append(features.cpu().detach())
        self.storage_feature = torch.cat(self.storage_feature,dim=0).cuda()
        storage_feature_np = self.storage_feature.cpu().numpy()
        self.pca = PCA(n_components=130)
        # Áp dụng PCA
        self.storage_feature_pca = self.pca.fit_transform(storage_feature_np)
        # Chuyển lại thành tensor
        self.storage_feature_pca = torch.tensor(self.storage_feature_pca).cuda()
        #Sampling Random
        self.storage_feature_final = self.storage_feature_pca.clone()
        selected_indices = np.random.choice(len(self.storage_feature_final), size=int(len(self.storage_feature_final)//float(self.parent.leditSizeEstablish.text())), replace=False)
        self.storage_feature_final = self.storage_feature_final[selected_indices]
        print("Kích thước của storage_feature_final:", list(self.storage_feature_final.shape))
        self.parent.lbDataSize.setText(str(list(self.storage_feature_final.shape)))
        self.parent.btnTraningModel.setEnabled(True)
        self.SetStyleSheetForbtn("btnTraningModel", "#DF2026")

    def TrainingModel(self):
        self.SetStyleSheetLable("label_92", "#DF2026")
        #totalbad
        #bad
        folder_path = Path(self.default_directory) / 'test'
        self.train_thread = Worker(folder_path, self.transform, self.backbone, self.pca, self.storage_feature_final)
        self.train_thread.finished.connect(self.on_train_thread)
        self.train_thread.start()
        
    def on_train_thread(self, y_score1, y_true1):
        #Lấy chỉ số AUC và confusion matrix, threshold
        # Calculate AUC-ROC score
        auc_roc_score1 = roc_auc_score(y_true1, y_score1)
        error = 1 - auc_roc_score1
        #Hiển thị giá trị % của AUC-ROC
        self.parent.lbPrecision.setText(f"{auc_roc_score1 * 100:.2f}%")
        self.parent.lbError.setText(f"{error * 100:.2f}%")
        # Plot ROC curve
        fpr, tpr, thresholds = roc_curve(y_true1, y_score1)
        # No plotting code for the ROC curve to focus on confusion matrix

        # F1 scores for different thresholds
        f1_scores = [f1_score(y_true1, y_score1 >= threshold) for threshold in thresholds]

        # Select the best threshold based on F1 score
        self.best_threshold = thresholds[np.argmax(f1_scores)]
        print(f"Best threshold: {self.best_threshold}")
        # Generate confusion matrix using the best threshold
        cm = confusion_matrix(y_true1, (y_score1 >= self.best_threshold).astype(int))

        # Extract confusion matrix components (TP, FP, TN, FN)
        TP = cm[0, 0]  # True Negatives
        FP = cm[0, 1]  # False Positives
        FN = cm[1, 0]  # True Positives
        TN = cm[1, 1]  # False Negatives
        self.parent.lbTP.setText(str(TP))
        self.parent.lbFP.setText(str(FP))
        self.parent.lbTN.setText(str(TN))
        self.parent.lbFN.setText(str(FN))
        self.ResultScreening()
        self.SetStyleSheetLable("label_92", "#A4A4A4")
        self.parent.btnConfirmModel.setEnabled(True)
        self.SetStyleSheetForbtn("btnConfirmModel", "#0055FF")
        self.parent.btnTryingTrain.setEnabled(True)
        self.SetStyleSheetForbtn("btnTryingTrain", "#33D909")
        self.parent.btnResultScreening.setEnabled(True)
        self.SetStyleSheetForbtn("btnResultScreening", "#0055FF")
    
    def ConfirmModel(self):
        #Lưu mô hình đã huấn luyện vào cơ sở dữ liệu
        torch.save(self.storage_feature_final, os.path.join(self.model_path, f'storage_feature_yellow_{self.position_name}_pri.pt'))
        joblib.dump(self.pca, os.path.join(self.model_path, f'pca_yellow_{self.position_name}_pri.pkl'))  # Lưu pca đã fit
        #Reset lại các thông số
        self.parent.btnConfirmModel.setEnabled(False)
        self.SetStyleSheetForbtn("btnConfirmModel", "#A4A4A4")
        self.parent.btnTryingTrain.setEnabled(False)
        self.SetStyleSheetForbtn("btnTryingTrain", "#A4A4A4")
        self.parent.btnResultScreening.setEnabled(False)
        self.SetStyleSheetForbtn("btnResultScreening", "#A4A4A4")
        self.parent.btnTraningModel.setEnabled(False)
        self.SetStyleSheetForbtn("btnTraningModel", "#A4A4A4")
        self.parent.lbDataSize.setText("")
        self.parent.lbTP.setText("")
        self.parent.lbFP.setText("")
        self.parent.lbTN.setText("")
        self.parent.lbFN.setText("")
        self.parent.lbPrecision.setText("")
        self.parent.lbError.setText("")
        self.parent.btnEstablish.setEnabled(False)
        self.SetStyleSheetForbtn("btnEstablish", "#A4A4A4")
        self.parent.leditSizeEstablish.setEnabled(False)
        self.parent.leditSizeEstablish.setText("")
        self.parent.btnSaveData.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveData", "#A4A4A4")
        self.parent.lbGoodTraining.setText("")
        self.parent.lbGoodTesting.setText("")
        self.parent.lbBadTesting.setText("")
        self.parent.lbTrained.setText("")
        self.parent.lbImage.clear()
        self.parent.lbHeatmap.clear()
        #Lưu lại best_threshold vào cơ sở dữ liệu
        c = self.conn.cursor()
        column_name = None
        if self.position_name == 'bl':
            column_name = 'ScoreBL'
        elif self.position_name == 'br':
            column_name = 'ScoreBR'
        elif self.position_name == 'mid':
            column_name = 'ScoreMID'
        elif self.position_name == 'tl':
            column_name = 'ScoreTL'
        elif self.position_name == 'tr':
            column_name = 'ScoreTR'
        if column_name:
            # Cập nhật giá trị best_threshold vào cột tương ứng
            c.execute(f"UPDATE Product SET {column_name} = ? WHERE ProductName = ?", (float(self.best_threshold), self.parent.lbTubeName_4.text()))
            self.conn.commit()  # Lưu thay đổi vào cơ sở dữ liệu
        else:
            print(f"Invalid position name: {self.position_name}")    
        #Mở thư mục chứa mô hình đã lưu
        subprocess.run(f'explorer "{self.model_path}"', shell=True)    
    
    def ResultScreening(self):
        self.backbone.eval()
        folder_path = Path(self.default_directory) / 'eval'
        for path in folder_path.glob('*.bmp'):  # Tìm các tệp .bmp trong thư mục 'bad'
            # Dự đoán với mô hình
            with torch.no_grad():
                img = cv2.imread(path)
                pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                data = self.transform(pil_image).cuda().unsqueeze(0)
                features = self.backbone(data)
                features1_np = features.cpu().numpy()
                features1_pca = self.pca.transform(features1_np)  # Không dùng .fit_transform ở đây!
                features1_pca_tensor = torch.from_numpy(features1_pca).cuda() 
            # Tính toán khoảng cách
            distances = torch.cdist(features1_pca_tensor, self.storage_feature_final, p=2.0)
            dist_score, dist_score_idxs = torch.min(distances, dim=1)
            s_star = torch.max(dist_score)
            # Tạo segmentation map
            segm_map = dist_score.view(1, 1, 28, 28)
            segm_map = torch.nn.functional.interpolate(
                segm_map,
                size=(224, 224),
                mode='bilinear'
            ).cpu().squeeze().numpy()

            # Sử dụng best_threshold để làm phân tách heatmap
            heatmap = np.zeros_like(segm_map)  # Khởi tạo heatmap rỗng
            heatmap[(segm_map >= self.best_threshold) & (segm_map <= self.best_threshold * 1.5)] = 1  # Điểm bất thường sẽ có giá trị = 1
            # Tính điểm bất thường
            y_score_image = s_star.cpu().numpy()
            y_pred_image = 1 * (y_score_image >= self.best_threshold)
            class_label = ['GOOD', 'BAD']
            # In kết quả
            print(f'File name: {path.name}')
            print(f'Anomaly score: {y_score_image:0.8f}')
            print(f'Prediction: {class_label[y_pred_image]}')
            text = class_label[y_pred_image]
            height, width, channel = img.shape
            font = cv2.FONT_HERSHEY_SIMPLEX
            # Cỡ chữ và độ dày của chữ
            font_scale = 0.5
            thickness = 1

            # Tính toán kích thước văn bản để căn giữa
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
            text_x = int((width - text_width) / 2)  # Tính toán vị trí x để căn giữa
            text_y = int((height + text_height) / 2)  # Tính toán vị trí y để căn giữa

            # Đặt văn bản vào chính giữa
            cv2.putText(img, text, (text_x, text_y), font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)

            y_score_text = f"{y_score_image:0.8f}"
            (text_width, text_height), _ = cv2.getTextSize(y_score_text, font, font_scale, thickness)
            text_x_2 = int((width - text_width) / 2)  # Tính toán vị trí x để căn giữa cho dòng văn bản thứ hai
            text_y_2 = text_y + text_height + 10  # Đặt văn bản thứ hai bên dưới văn bản đầu tiên

            # Đặt dòng văn bản thứ hai vào chính giữa
            cv2.putText(img, y_score_text, (text_x_2, text_y_2), font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)
            # Chuyển heatmap từ NumPy array thành QImage
            heatmap_display = np.uint8(255 * heatmap)  # Chuẩn hóa heatmap từ 0 đến 255
            self.image_list.append(img)
            self.heatmap_list.append(heatmap_display)
            
    def update_image(self):
        # Cập nhật hình ảnh và heatmap khi nhấn nút (Đi lên hoặc đi xuống)
        if len(self.image_list) == 0:
            return  # Nếu không có hình ảnh, không làm gì

        # Lấy hình ảnh và heatmap theo index hiện tại
        img_for_display = self.image_list[self.current_index]
        heat_map = self.heatmap_list[self.current_index]

        # Hiển thị hình ảnh lên Qt (ví dụ: QLabel)
        height, width, channel = img_for_display.shape
        bytes_per_line = 3 * width
        q_image = QImage(img_for_display, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)

        # Hiển thị ảnh gốc trên QLabel (giả sử QLabel là self.parent.lbImage)
        scaled_pixmap = pixmap.scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.parent.lbImage.setPixmap(scaled_pixmap)

        heatmap_qimage = QImage(heat_map.data, heat_map.shape[1], heat_map.shape[0], heat_map.strides[0], QImage.Format.Format_Grayscale8)
        heatmap_pixmap = QPixmap.fromImage(heatmap_qimage)
        
        # Hiển thị heatmap trên QLabel khác (giả sử QLabel là self.parent.lbHeatmap)
        scaled_heatmap_pixmap = heatmap_pixmap.scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.parent.lbHeatmap.setPixmap(scaled_heatmap_pixmap)

    def on_result_screening(self):
        # Cập nhật chỉ mục và hiển thị cặp đầu tiên
        if len(self.image_list) > 0:
            self.current_index = 0  # Cặp đầu tiên
            self.update_image()

    def on_next_button(self):
        # Cập nhật chỉ mục và hiển thị hình ảnh tiếp theo
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.update_image()

    def on_previous_button(self):
        # Cập nhật chỉ mục và hiển thị hình ảnh trước đó
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()
        else:
            # Nếu ở cặp đầu tiên, quay lại cặp cuối cùng
            self.current_index = len(self.image_list) - 1
            self.update_image()

    def TryTrainingModel(self):
        #Reset lại các thông số
        self.parent.btnConfirmModel.setEnabled(False)
        self.SetStyleSheetForbtn("btnConfirmModel", "#A4A4A4")
        self.parent.btnTryingTrain.setEnabled(False)
        self.SetStyleSheetForbtn("btnTryingTrain", "#A4A4A4")
        self.parent.btnResultScreening.setEnabled(False)
        self.SetStyleSheetForbtn("btnResultScreening", "#A4A4A4")
        self.parent.btnTraningModel.setEnabled(False)
        self.SetStyleSheetForbtn("btnTraningModel", "#A4A4A4")
        self.parent.lbDataSize.setText("")
        self.parent.lbTP.setText("")
        self.parent.lbFP.setText("")
        self.parent.lbTN.setText("")
        self.parent.lbFN.setText("")
        self.parent.lbPrecision.setText("")
        self.parent.lbError.setText("")
        self.parent.btnEstablish.setEnabled(False)
        self.SetStyleSheetForbtn("btnEstablish", "#A4A4A4")
        self.parent.leditSizeEstablish.setEnabled(False)
        self.parent.leditSizeEstablish.setText("")
        self.parent.btnSaveData.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveData", "#A4A4A4")
        self.parent.lbGoodTraining.setText("")
        self.parent.lbGoodTesting.setText("")
        self.parent.lbBadTesting.setText("")
        self.parent.lbTrained.setText("")
        self.parent.lbImage.clear()
        self.parent.lbHeatmap.clear()
        
    def SetupStyleTable(self, table):
        scrollbar_v = self.scrollbar("vertical", "ffffff", "0055FF")
        scrollbar_h = self.scrollbar("horizontal", "ffffff", "0055FF")
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setShowGrid(False)
        style = """
                QTableWidget {
                    background-color: #ffffff;  /* Màu nền bảng */
                    border-radius: 0px;  /* Bo tròn góc */
                    color: #0055FF;  /* Màu chữ */
                    font-family: Inter, sans-serif;
                    font-size: 14px;
                    font-weight: bold;
                    border: 1px solid #0055FF;
                }
                QTableWidget::item {
                    border: 1px solid #0055FF;  /* Viền đỏ cho tất cả ô */
                    font-family: Inter, sans-serif;
                    font-size: 14px;
                    font-weight: bold;
                }
                QHeaderView::section {
                background-color: #ffffff;
                border: 1px solid #0055FF;  /* Ẩn viền */
                font-weight: bold;
                font-family: Inter, sans-serif;
                font-size: 16px;
                }
                """
        full_style = style + scrollbar_v + scrollbar_h

        table.setStyleSheet(full_style)
    
    def scrollbar(self, direction, base_color, color):
        style = f"""
        QScrollBar:{direction} {{
            border: none; 
            background-color: #{base_color}; 
            {'width' if direction == 'vertical' else 'height'}: 10px; 
            margin: 0px 0px 0px 0px; 
        }}
        
        QScrollBar::handle:{direction} {{
            background-color: #{color}; 
            border-radius: 5px; 
        }}
        
        QScrollBar::handle:{direction}:hover {{
            background-color: #4D9EFF; 
        }}
        
        QScrollBar::add-line:{direction}, QScrollBar::sub-line:{direction} {{
            border: none; 
            background: none; 
        }}
        
        QScrollBar::add-page:{direction}, QScrollBar::sub-page:{direction} {{
            background: none;
        }}
        """
        return style

    def ShowProductList(self):
        self.cursor = self.conn.cursor()
        #Lấy dữ liệu ProductName, ScoreBL từ bảng Product
        self.cursor.execute("SELECT ProductName, ScoreBL, ScoreBR, ScoreMID, ScoreTL, ScoreTR FROM Product")
        product = self.cursor.fetchall()
        #Xóa tất cả các mục trong listWidget
        table = self.parent.tbProductList
        table.setRowCount(0)
        current_row_count = table.rowCount()
        table.verticalHeader().setVisible(False)
        # for row_idx, row_data in enumerate(product):
        #     table.insertRow(current_row_count + row_idx)  # Thêm hàng mới vào cuối bảng
            
        #     # Thêm cột số thứ tự vào cột đầu tiên (STT)
        #     item = QTableWidgetItem(str(current_row_count + row_idx + 1))  # Tính số thứ tự
        #     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        #     table.setItem(current_row_count + row_idx, 0, item)  # Đặt số thứ tự vào cột đầu tiên
            
        #     # Thêm các giá trị khác vào các cột còn lại
        #     for col_idx, value in enumerate(row_data):
        #         if col_idx < 8:  # Tránh việc truy cập ngoài phạm vi
        #             item = QTableWidgetItem(str(value))
        #             item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        #             table.setItem(current_row_count + row_idx, col_idx + 1, item)  # Đặt vào các cột sau cột số thứ tự
        for row_idx, row_data in enumerate(product):
            table.insertRow(current_row_count + row_idx)  # Thêm hàng mới
            
            # STT
            item = QTableWidgetItem(str(current_row_count + row_idx + 1))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(current_row_count + row_idx, 0, item)  
            # Tên sản phẩm
            item = QTableWidgetItem(str(row_data[0]))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(current_row_count + row_idx, 1, item)
            
            # Nhân viên thiết lập (thêm thủ công)
            employee_name = "Nguyễn Văn A"  # Hoặc lấy từ self.currentUser hoặc nơi bạn lưu tên nhân viên
            item = QTableWidgetItem(employee_name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(current_row_count + row_idx, 2, item)

            # Các chỉ số (ScoreBL, ScoreBR, ScoreMID, ScoreTL, ScoreTR)
            for col_idx, value in enumerate(row_data[1:], start=3):  # Bắt đầu từ cột thứ 4
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(current_row_count + row_idx, col_idx, item)

    def Push_working_history(self, action_name: str):
        action_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        c = self.conn.cursor()
        #Lưu vào database
        c.execute("INSERT INTO WorkingHistory (FullName, Duty, ActionName, ActionTime) VALUES (?, ?, ?, ?)",
                (self.initial.FullName[0], self.initial.Duty[0], action_name, action_time))
        self.conn.commit()
