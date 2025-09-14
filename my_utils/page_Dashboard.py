# from MainUI1 import Ui_MainWindow
# from page_Initial import PageInitialBackend
# from page_Parameter_ConfimDelay import PageParameterConfirmBackend
# from page_Parameter import PageParameterBackend
# from PyQt6.QtCore import QTimer, QDateTime
# from PyQt6 import QtCore
# import os
# from CubeDetection import load_model
# import torch
# import time
# from torchvision.transforms import transforms
# from torchvision.models import mobilenet_v3_large
# from worker_capture import CaptureAndDetectWorker
# from CheckingCamera import ConnectionCameraChecker
# from CheckingPLC import ConnectionPLCChecker
# import re 
# from pymelsec.constants import DT
# from pymelsec import Type3E
# import shutil
# from pymelsec.tag import Tag
# import gc
# import neoapi
# import joblib
# ########################################################################################################################################################################################
# class DashboardBackend():
#     def __init__(self, main: Ui_MainWindow, conn, initial: PageInitialBackend, para: PageParameterBackend, paraconfirm: PageParameterConfirmBackend):
#         self.parent = main
#         self.conn = conn
#         self.initial = initial
#         self.para = para
#         self.paraconfirm = paraconfirm
#         self.paraconfirm.set_confirm_page(self)
#         self.image_directory = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceImages" #Nơi chứa ảnh để thực hiện object detection
#         self.prediction = False
#         classes_to_filter = None  # You can give list of classes to filter by name, Be happy you don't have to put class number. ['train','person']
#         # Trước khi load model mới
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#             for attr in ['model', 'Backbone', 'MemoryBL', 'MemoryBR', 'MemoryMID', 'MemoryTL', 'MemoryTR']:
#                 if hasattr(self, attr):
#                     delattr(self, attr)
#         gc.collect()
#         torch.cuda.synchronize()
#         self.opt = {
#             "weights": r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\yolov7.torchscript.pt",  # Path to weights file default weights are for nano model
#             "img-size": 576,  # default image size
#             "conf-thres": 0.5,  # confidence threshold for inference.
#             "iou-thres": 0.45,  # NMS IoU threshold for inference.
#             "device": '0' if torch.cuda.is_available() else 'cpu',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
#             "classes": classes_to_filter  # list of classes to filter or None
#         }
#         self.model, self.device, self.half, self.stride, self.imgsz = load_model(self.opt)
#         self.image_paths = [os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
#         self.capture_thread = None
#         self.checking_camera_thread = None 
#         self.checking_plc_thread = None
#         self.Total = 0
#         self.Bad = 0
#         self.Good = 0
#         self.Row = []
#         self.Col = []
#         self.DefectiveTotal = 0
#         self.ShortageTotal = 0
#         self.filename = None
#         self.ScoreBL = 0
#         self.ScoreBR = 0
#         self.ScoreMID = 0
#         self.ScoreTL = 0
#         self.ScoreTR = 0
#         self.failed_labels = []
#         self.error_logs = []
#         self.End_Time = None
#         # self.parent.lbTotal.setText("0")
#         # self.parent.label_204.setText("0")
#         # self.parent.label_203.setText("0")
#         # self.parent.lbDefectiveTotal.setText("0")
#         # self.parent.lbShortageTotal.setText("0")
#         # self.parent.lbTimeCounter.setText("0")
#         # self.parent.lbTimeDetect.setText("0")
#         #Update Database
#         self.UpdateDB(self.parent.lbProductName1.text())
#         #Tải mô hình anomaly detection
#         if self.filename and self.filename[0]:
#             self.Backbone, self.MemoryBL, self.MemoryBR, self.MemoryMID, self.MemoryTL, self.MemoryTR, self.Transform, self.pca_bl, self.pca_br, self.pca_mid, self.pca_tl, self.pca_tr = self.SetupAnomalyDetection()
        
#         #Disable các nút ban đầu
#         self.parent.btnDashboard.setEnabled(True)
#         self.parent.btnDashboard1.setEnabled(True)
#         self.parent.btnReset.setEnabled(False)
#         self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
#         self.parent.btnStop.setEnabled(False)
#         self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
#         self.parent.btnRestart.setEnabled(False)
#         self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
#         self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
#         #Nút nhấn Run và Stop
#         self.Running = False
#         self.parent.btnRun.clicked.connect(self.RunSystem)
#         self.parent.btnStop.clicked.connect(self.StopSystem)
#         self.parent.btnLogout.clicked.connect(lambda: [self.StopSystem(), self.Push_working_history("Đăng xuất")])
#         #Chớp tắt
#         self.blink_timer = QTimer()
#         self.blink_timer.timeout.connect(self.blink_effect)
#         self.blink_count = 0
#         self.blink_colors = ["#DF2026", "#A4A4A4"]  # Đỏ - Xám
#         #Kiểm tra kết nối liên tục
#         self.CheckCameraConnectionTimer = QTimer()
#         self.CheckCameraConnectionTimer.timeout.connect(self.CheckCameraConnection)
#         self.CheckCameraConnectionTimer.start(5000)  # Kiểm tra mỗi giây
#         self.CheckPLCConnectionTimer = QTimer()
#         self.CheckPLCConnectionTimer.timeout.connect(self.CheckPLCConnection)
#         self.CheckPLCConnectionTimer.start(5000)  # Kiểm tra mỗi giây
#         self.CheckSystemConnectionTimer = QTimer()
#         self.CheckSystemConnectionTimer.timeout.connect(self.CheckSystemConnection)
#         self.CheckSystemConnectionTimer.start(1000)  # Kiểm tra mỗi giây
   
#         #Nút nhấn Restart
#         self.btnRestartPressed = False
#         self.parent.btnRestart.clicked.connect(lambda: [self.RestartSystem(), self.parent.btnRestart.setEnabled(False), self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px"), self.UpdateSystemStatus()])
#         #Nút nhấn Reset
#         self.btnResetPressed = False 
#         self.parent.btnReset.clicked.connect(lambda: [self.EnableRestart()])
#         #Hiển thị tên sản phẩm được chọn từ page Parameter Confirm
#         self.parent.lbTubeName.setText(self.parent.label_56.text())
#         #Chạy Trigger
#         self.TriggerPredict = QTimer()
#         self.TriggerPredict.timeout.connect(self.CaptureAndDetect)
#         self.UpdateManufactoringTime = QTimer()
#         self.UpdateManufactoringTime.timeout.connect(self.UpdateManufactoring)
#         self.UpdateManufactoringTime.start(5000)  # Cập nhật mỗi giây
        
#     #Set style cho label    
#     def SetStyleSheetLable(self, object, background_color):
#         #Style cho nút btnEmployeeWorking
#         button = getattr(self.parent, object)
#         button.setStyleSheet(f"""
#                 QLabel#{object} {{
#                     border-radius: 15px;
#                     background-color: {background_color};  /* Màu nền mới */
#                     color: white;
#                     text-align: center;
#                     font-family: Inter, sans-serif;
#                     border: 1px solid #ffffff;
#                 }}""")
#     #Set style cho nút
#     def SetStyleSheetForbtn(self, btn, background_color,pixel):
#         #Style cho nút 
#         button = getattr(self.parent, btn)
#         button.setStyleSheet(f"""
#                 QPushButton#{btn} {{
#                     border-radius: {pixel};
#                     border-color: white;
#                     background-color: {background_color};  /* Màu nền mới */
#                     color: white;
#                     text-align: center;
#                     font-family: Inter, sans-serif;
#                     opacity: 0.7;
#                     border: 1px solid #FFFFFF;
#                 }}

#                 QPushButton#{btn}:hover {{
#                     background-color: #FFA500;  /* Màu nền khi hover */
#                 }}

#                 QPushButton#{btn}:pressed {{
#                     padding-left: 5px;
#                     padding-top: 5px;
#                 }}
#                 """)
#     #Chạy hệ thống
#     def RunSystem(self):
#         self.Push_working_history("Bắt đầu hệ thống")
#         self.SetStyleSheetLable("lbStatusSystem", "#33D909")
#         # self.parent.lbStatusSystem.setText("ONLINE")
#         self.parent.btnRun.setEnabled(False)
#         self.SetStyleSheetForbtn("btnRun", "#A4A4A4", "15px")
#         self.parent.btnStop.setEnabled(True)
#         self.SetStyleSheetForbtn("btnStop", "#F23030", "15px")
#         # self.ResetLable()

#         self.capture_thread = CaptureAndDetectWorker(self, self.initial, self.parent,self.paraconfirm, self.model, 
#                                                     self.device, 
#                                                     self.half, 
#                                                     self.stride, 
#                                                     self.imgsz, 
#                                                     self.opt, 
#                                                     self.image_directory
#                                                     )
#         self.capture_thread.finished.connect(self.onCaptureFinished)
#         #Thực tế
#         self.TriggerPredict.start(10)   
#         self.WritePlcVariable("M4020",1)
#     #Dừng hệ thống
#     def StopSystem(self):
#         # self.Push_working_history("Dừng hệ thống")
#         self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
#         self.parent.btnRun.setEnabled(True)
#         self.SetStyleSheetForbtn("btnRun", "#33D909", "15px")
#         self.parent.btnStop.setEnabled(False)
#         self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
#         self.End_Time = QtCore.QDateTime.currentDateTime()
#         print("Time_End: ", self.End_Time.toString("yyyy-MM-dd hh:mm:ss"))
#         self.UpdateHistoryTime()
#         self.TriggerPredict.stop()
#         # self.WritePlcVariable("M4020", 0)
#     #Kết nối PLC
#     def PLCConnection(self,plc_host, plc_port, plc_type):
#         print("Checking PLC connection...")
#         print("PageInitialBackend.PLCConnected:", PageInitialBackend.PLCConnected)
#         if PageInitialBackend.PLCConnected:
#             return True
#         try:
#             PageInitialBackend.Plc = Type3E(host=plc_host, port=plc_port, plc_type=plc_type)
#             PageInitialBackend.Plc.set_access_opt(comm_type='binary')
#             PageInitialBackend.Plc.connect(ip=plc_host, port=plc_port)
#             print("Connecting to PLC.")
#             PageInitialBackend.PLCConnected = True
#             self.WritePlcVariable("M4022", 1)

#             self.CheckPLCConnectionTimer.start(5000)
#         except Exception as e:
#             print(f"Error connecting to PLC: {e}")
#             PageInitialBackend.PLCConnected = False
#             return False
#     #Kết nối camera
#     def CameraConnection(self):
#         # Kiểm tra xem camera đã kết nối hay chưa
#         print("Checking camera connection...")
#         print("PageInitialBackend.CameraConnected:", PageInitialBackend.CameraConnected)
#         if PageInitialBackend.CameraConnected:
#             return True
#         try:
#             PageInitialBackend.Camera = neoapi.Cam()
#             PageInitialBackend.Camera.Connect()   
#             PageInitialBackend.CameraName = PageInitialBackend.Camera.GetFeature("DeviceModelName").GetString()
#             print(f"Camera connected: {PageInitialBackend.CameraName}")
#             if PageInitialBackend.Camera.IsConnected():
#                 print("Connecting to Camera.")
#                 PageInitialBackend.CameraConnected = True
#                 self.CheckCameraConnectionTimer.start(5000)
#                 return True
#             else:
#                 PageInitialBackend.CameraConnected = False
#                 raise Exception("Camera not connected.")
#         except (neoapi.NeoException, Exception) as e:
#             print(f"Error checking camera connection1: {e}")
#             PageInitialBackend.CameraConnected = False
#             return False
#     #Kiểm tra kết nối camera
#     def CheckCameraConnection(self):
#         self.checking_camera_thread = ConnectionCameraChecker(self.initial.CheckCameraConnection)
#         self.checking_camera_thread.finished.connect(self.onCameraConnectionChecked)
#         self.checking_camera_thread.start()
#         if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#             self.parent.btnRestart.setEnabled(False)
#             self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
#             # self.parent.btnReset.setEnabled(False)
#             # self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
#     #Kiểm tra kết nối PLC
#     def CheckPLCConnection(self):
#         self.checking_plc_thread = ConnectionPLCChecker(self.initial.CheckPLCConnection)
#         self.checking_plc_thread.finished.connect(self.onPLCConnectionChecked)
#         self.checking_plc_thread.start()
#         if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#             self.parent.btnRestart.setEnabled(False)
#             self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
#             # self.parent.btnReset.setEnabled(False)
#             # self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
#     #Kiểm tra kết nối hệ thống
#     def CheckSystemConnection(self):
#         if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#             self.parent.btnRestart.setEnabled(False)
#             self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
#             # self.parent.btnReset.setEnabled(False)
#             # self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
#             self.SetStyleSheetLable("lbCameraConnected", "#33D909")
#             self.SetStyleSheetLable("lbPLCConnected", "#33D909")
#     #Thực thi kiểm tra kết nối camera
#     def onCameraConnectionChecked(self, result):
#         if result:
#             self.SetStyleSheetLable("lbCameraConnected", "#33D909")
#         else:
#             self.CheckCameraConnectionTimer.stop()  # Dừng kiểm tra kết nối khi nhấn
#             self.TriggerPredict.stop()
#             # self.WritePlcVariable("M4001", 1)
#             self.WritePlcVariable("M4020",0)
#             self.failed_labels.append("lbCameraConnected")
#             self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
#             self.parent.btnRun.setEnabled(False)
#             self.SetStyleSheetForbtn("btnRun", "#A4A4A4", "15px")
#             self.parent.btnStop.setEnabled(False)
#             self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
#             self.parent.btnReset.setEnabled(True)
#             self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
#             self.Error_Camera_Time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
#             self.UpdateErrorCamera(self.Error_Camera_Time)
#             if self.failed_labels:
#                 self.blink_count = 0
#                 self.blink_timer.start(500)
#                 self.parent.btnReset.setEnabled(True)
#                 self.SetStyleSheetForbtn("btnReset", "#FFDE21", "15px")
#     #Thực thi kiểm tra kết nối PLC
#     def onPLCConnectionChecked(self, result):
#         if result:
#             self.SetStyleSheetLable("lbPLCConnected", "#33D909")
#             # self.WritePlcVariable("M4022",1)
#         else:
#             print("ABC")
#             PageInitialBackend.Plc.close()
#             self.CheckPLCConnectionTimer.stop()
#             self.checking_plc_thread.exit()
#             self.checking_plc_thread.wait()
#             self.TriggerPredict.stop()
#             self.failed_labels.append("lbPLCConnected")
#             self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
#             self.parent.btnRun.setEnabled(False)
#             self.SetStyleSheetForbtn("btnRun", "#A4A4A4", "15px")
#             self.parent.btnStop.setEnabled(False)
#             self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
#             self.parent.btnReset.setEnabled(True)
#             self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
#             self.Error_PLC_Time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
#             self.UpdateErrorPLC(self.Error_PLC_Time)
#             if self.failed_labels:
#                 self.blink_count = 0
#                 self.blink_timer.start(500)
#                 self.parent.btnReset.setEnabled(True)
#                 self.SetStyleSheetForbtn("btnReset", "#FFDE21", "15px")
#     #Nhấp nháy đèn báo lỗi
#     def blink_effect(self):
#         color = self.blink_colors[self.blink_count % 2]  # Chọn màu
#         for label in self.failed_labels:
#             self.SetStyleSheetLable(label, color)
#         self.blink_count += 1
#     #Restart hệ thống - Khởi động lại hệ thống
#     def RestartSystem(self):
#         self.Push_working_history("Nhấn nút khởi động lại hệ thống")
#         self.failed_labels = []
#         self.btnRestartPressed = True
#         #Thực tế
#         if not PageInitialBackend.PLCConnected:
#             self.PLCConnection(self.parent.leditPLCHost.text(), int(self.parent.leditPLCPort.text()), self.parent.leditPLCType.text())
#         if not PageInitialBackend.CameraConnected:
#             self.CameraConnection()
#         print("PLC Connected1:", PageInitialBackend.PLCConnected)
#         print("Camera Connected1:", PageInitialBackend.CameraConnected)
#         self.para.SetupCameraForTrigger()
#         if PageInitialBackend.PLCConnected:
#             self.SetStyleSheetLable("lbPLCConnected", "#33D909")
#         else:
#             self.failed_labels.append("lbPLCConnected")
#         if PageInitialBackend.CameraConnected:
#             self.SetStyleSheetLable("lbCameraConnected", "#33D909")
#         else:
#             self.failed_labels.append("lbCameraConnected")
#         if self.failed_labels:
#             self.blink_timer.start(500)
#             self.parent.btnReset.setEnabled(True)
#             self.SetStyleSheetForbtn("btnReset", "#FFDE21", "15px")
#         if (not PageInitialBackend.PLCConnected or not PageInitialBackend.CameraConnected) and self.btnRestartPressed:
#             self.parent.btnReset.setEnabled(True)
#             self.SetStyleSheetForbtn("btnReset", "#FFDE21", "15px")
#         else:
#             self.parent.btnRun.setEnabled(True)
#             self.SetStyleSheetForbtn("btnRun", "#33D909", "15px")
#             self.parent.btnRestart.setEnabled(False)
#             self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
#         self.CheckCameraConnectionTimer.start(5000)  # Kiểm tra mỗi 
#         self.CheckPLCConnectionTimer.start(5000)  # Kiểm tra mỗi giây
#     #Cho phép nhấn nút tắt đèn cảnh báo
#     def EnableRestart(self):
        
#         self.Push_working_history("Nhấn nút tắt đèn cảnh báo")
#         self.btnResetPressed = True
#         if (not PageInitialBackend.PLCConnected or not PageInitialBackend.CameraConnected) and self.btnResetPressed:
#             self.parent.btnRestart.setEnabled(True)
#             self.SetStyleSheetForbtn("btnRestart", "#F68013", "15px")
#             self.CheckCameraConnectionTimer.stop()  # Dừng kiểm tra kết nối khi nhấn Reset
#             self.CheckPLCConnectionTimer.stop()  # Dừng kiểm tra kết nối khi nhấn Reset
#             self.parent.btnReset.setEnabled(False)  # Ẩn nút Reset sau khi nhấn
#             self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
#             self.blink_timer.stop()
#             for label in self.failed_labels:
#                 self.SetStyleSheetLable(label, "#A4A4A4")  # Đổi về màu xám
#             self.failed_labels.clear()  # Xóa danh sách lỗi
#             self.RestartSystem()
#             # self.WritePlcVariable("M4021",1)
#         else: 
#             # Tắt đèn tháp và xy lanh (làm sau)
#             # self.WritePlcVariable("M4021",1)
#             # Tắt nút btnReset
#             self.parent.btnReset.setEnabled(False)  # Ẩn nút Reset sau khi nhấn
#             self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
#     #Update trạng thái hệ thống ở trang Initial
#     def UpdateSystemStatus(self):
#         if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#             self.parent.btnSystemConnection.setEnabled(False)
#             self.parent.btnSystemConnection.setText("Đã kết nối")
#             self.initial.SetStyleSheetLable("lbPLCConnected_2", "#33D909")
#             self.initial.SetStyleSheetLable("lbCameraConnected_2", "#33D909")
#         elif PageInitialBackend.PLCConnected and not PageInitialBackend.CameraConnected:
#             self.parent.btnSystemConnection.setEnabled(True)
#             self.parent.btnSystemConnection.setText("Kết nối hệ thống")
#         elif not PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#             self.parent.btnSystemConnection.setEnabled(True)
#             self.parent.btnSystemConnection.setText("Kết nối hệ thống")
#     #Lấy tên tệp hình ảnh tiếp theo
#     def GetNextFilename(self):
#         # Kiểm tra thư mục tồn tại
#         if not os.path.exists(self.image_directory):
#             print(f"Directory not found, creating: {self.image_directory}")
#             os.makedirs(self.image_directory)  # Tạo thư mục nếu không tồn tại

#         current_datetime = QDateTime.currentDateTime()
#         formatted_datetime = current_datetime.toString("yyyy-MM-dd-hh-mm-ss")
#         filename = f"{formatted_datetime}_IMG.bmp"
#         file_path = os.path.join(self.image_directory, filename)

#         return file_path
#     #Thực hiện lấy ảnh từ camera và làm object detection
#     def CaptureAndDetect(self):
#         if PageInitialBackend.CameraConnected and PageInitialBackend.PLCConnected:
#             self.paraconfirm.GetPlcVariableForTrigger()
#             # print("Waiting for next trigger")
#             if self.paraconfirm.triggered:
#                 self.TriggerPredict.stop()  # Dừng TriggerPredict 
#                 self.paraconfirm.processing = True
#                 print("Trigger activated, processing images...")
#                 self.ResetLable()
#                 self.CheckCameraConnectionTimer.stop()  # Dừng kiểm tra kết nối khi nhấn
#                 self.CheckPLCConnectionTimer.stop()  # Dừng kiểm tra kết nối khi nhấn
#                 print("self.paraconfirm.Delay[0]:", self.paraconfirm.Delay[0])
#                 try:
#                     time.sleep(self.paraconfirm.Delay[0])
#                     if self.para.trigger:
#                         print("Trigger is initialized.")
#                         self.para.trigger.Execute()
#                     else:
#                         print("Trigger is not initialized.")            
#                     img_camera = PageInitialBackend.Camera.GetImage()
#                     if img_camera is None:
#                         print("Failed to capture image from camera.")
#                     else:
#                         print("Image captured successfully.")
#                         time.sleep(0.1)  
#                         file_path = self.GetNextFilename()
#                         img_camera.Save(file_path)
#                     #Kiểm tra đường dẫn ảnh đã lưu hay chưa
#                     self.check_timer = QTimer()
#                     self.check_timer.setInterval(100)  # 10ms
#                     self.check_timer.timeout.connect(self.check_image_saved(file_path))
#                     self.check_timer.start()

#                     self.paraconfirm.triggered = False  # Đặt lại trigger để chờ lần kích hoạt tiếp theo
#                     self.paraconfirm.processing = False 
#                 except Exception as e:
#                     print(f"Error capturing or saving image: {e}")
#                     self.TriggerPredict.start(10)  # Bắt đầu lại việc kiểm tra ảnh
#                 finally:
#                     self.paraconfirm.triggered = False  # Đặt lại trigger để chờ lần kích hoạt tiếp theo
#                     self.paraconfirm.processing = False
#             else:
#                 if self.capture_thread.isRunning():
#                     self.capture_thread.exit()
#                     self.capture_thread.wait()
#         else:
#             print("Camera or PLC is not connected.")  
   
#     def check_image_saved(self, file_path):
#         if os.path.exists(file_path):
#             self.check_timer.stop()
#             print(f"Image saved successfully at {file_path}.")
#             if not self.capture_thread.isRunning():
#                 self.capture_thread.start() 

#     #Tải mô hình phát hiện bất thường
#     def SetupAnomalyDetection(self):
#         print("Setting up anomaly detection...")
#         Transform = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor()])
#         class mobilenet_feature_extractor(torch.nn.Module):
#             def __init__(self):
#                 super(mobilenet_feature_extractor, self).__init__()
#             # Tải mô hình MobileNetV3 với trọng số đã huấn luyện
#                 self.model = mobilenet_v3_large(pretrained=True)

#                 # Đặt chế độ đánh giá và tắt gradient
#                 self.model.eval()
#                 for param in self.model.parameters():
#                     param.requires_grad = False

#                 # Hook để trích xuất feature maps
#                 self.features = []
#                 def hook(module, input, output):
#                     """Lưu lại các feature maps từ các tầng cụ thể."""
#                     self.features.append(output)

#                 # Đăng ký hook vào các tầng mà bạn muốn trích xuất feature maps
#                 self.model.features[3].register_forward_hook(hook)  # Tầng giữa (middle layer)
#                 self.model.features[6].register_forward_hook(hook)  # Tầng sâu hơn (deeper layer)
#                 self.model.features[12].register_forward_hook(hook) # Một tầng sâu hơn nữa (deep layer)

#             def forward(self, input):
#                 """Truyền đầu vào qua mô hình và thu thập feature maps."""
#                 self.features = []  # Để lưu các feature maps
#                 with torch.no_grad():
#                     _ = self.model(input)  # Truyền qua mô hình

#                 # Feature maps từ các hook
#                 resized_maps = [
#                     torch.nn.functional.adaptive_avg_pool2d(fmap, (28, 28)) for fmap in self.features
#                 ]
#                 patch = torch.cat(resized_maps, 1)  # Nối các feature maps
#                 patch = patch.reshape(patch.shape[1], -1).T  # Chuyển thành tensor dạng cột

#                 return patch
#         Backbone = mobilenet_feature_extractor().cuda()
#         # Kiểm tra nếu truy vấn trả về kết quả hợp lệ
#         if self.filename and self.filename[0]: 
#             print("Filename:", self.filename[0])         
#             # Tìm màu bằng regex (màu là phần đầu tiên trước từ "PLASTIC")
#             match = re.match(r"([A-Z]+)PLASTIC", self.filename[0])
#             if match:
#                 color = match.group(1).lower()  # Lấy màu và chuyển thành chữ thường
                
#                 # Định nghĩa các vị trí model cần tải
#                 positions = ["bl", "br", "mid", "tl", "tr"]

#                 # Tạo và tải model động
#                 base_path = rf"H:\HK242\LVTN\Model\{self.filename[0]}\memory_bank_{color}_"
#                 base_path_pca = rf"H:\HK242\LVTN\Model\{self.filename[0]}\pca_{color}_"
#                 models = {}
#                 models_pca = {}
#                 try:
#                     for pos in positions:
#                         model_path = base_path + f"{pos}_final.pt"
#                         model_path_pca = base_path_pca + f"{pos}.pkl"
#                         # model_path = base_path + f"{pos}_pca.pt"
#                         models[pos.upper()] = torch.load(model_path).cuda()
#                         models_pca[pos.upper()] = joblib.load(model_path_pca)
#                         #Hiển thị shape của model
#                         print(f"Model {pos.upper()} shape:", models[pos.upper()].shape)
#                     # Giải nén dictionary vào các biến MemoryBL, MemoryBR...
#                     MemoryBL, MemoryBR, MemoryMID, MemoryTL, MemoryTR = (
#                         models["BL"], models["BR"], models["MID"], models["TL"], models["TR"]
#                     )
#                     # Giải nén dictionary vào các biến pca_bl, pca_br...
#                     pca_bl, pca_br, pca_mid, pca_tl, pca_tr = (
#                         models_pca["BL"], models_pca["BR"], models_pca["MID"], models_pca["TL"], models_pca["TR"]
#                     )
#                 except FileNotFoundError as e:
#                     print(f"Lỗi: Không tìm thấy model {model_path} - {e}")
#             else:
#                 print(f"Lỗi: Không tìm thấy màu trong '{self.filename}'!")
#         else:
#             print("Lỗi: Không lấy được tên file từ database!")
#         return Backbone, MemoryBL, MemoryBR, MemoryMID, MemoryTL, MemoryTR, Transform, pca_bl, pca_br, pca_mid, pca_tl, pca_tr
#     #Thực thi điều chỉnh UI khi hoàn tất 
#     def onCaptureFinished(self, bad_pos, shortage_pos, DefectiveTime, ShortageTime):
#         print("Capture finished")
#          #Kiểm tra trong 100 ô có ô nào màu xám nữa không
#         gray_color = "#A4A4A4"
#         found_labels = []
#         self.failed_plc = len(bad_pos) + len(shortage_pos)
#         # self.WritePlcVariableWord("D4525",int(self.failed_plc))
#         # self.WritePlcVariableWord("D4521", 100 - int(self.failed_plc))
#         for i in range(1, 101):
#             label_name = f"lbPos{i}"
#             label = getattr(self.parent, label_name, None)
#             if label:
#                 current_style = label.styleSheet()
#                 if gray_color.lower() in current_style.lower():
#                     found_labels.append(label_name)
#         # Đặt màu theo điều kiện số lượng label
#         new_color = "#F68013" if len(found_labels) > 50 else "#33D909"
#         # Cập nhật màu cho các label tìm được
#         for label_name in found_labels:
#             self.SetStyleSheetLable(label_name, new_color)
#         self.CheckCameraConnectionTimer.start(5000)  # Kiểm tra lại kết nối camera sau khi nhấn
#         self.CheckPLCConnectionTimer.start(5000)  # Kiểm tra lại kết nối PLC sau khi nhấn
#         print("Bad positions:", bad_pos)
#         print("Shortage positions:", shortage_pos)
#         print("DefectiveTime:", DefectiveTime)
#         print("ShortageTime:", ShortageTime)
#         self.DefectiveTotal += len(bad_pos) 
#         self.ShortageTotal += len(shortage_pos)
#         self.parent.lbDefectiveTotal.setText(str(self.DefectiveTotal))
#         self.parent.lbShortageTotal.setText(str(self.ShortageTotal))
#         self.Bad += len(bad_pos) + len(shortage_pos)
#         self.Good = self.Total - self.Bad
#         self.parent.label_204.setText(str(self.Bad))
#         self.parent.label_203.setText(str(self.Good))
#         #Xóa file ảnh đã lưu ở thư mục SourceImages
#         self.TriggerPredict.start(10)  # Bắt đầu lại việc kiểm tra ảnh

#         while len(bad_pos) > len(DefectiveTime):
#             qt_times = [QtCore.QDateTime.fromString(t, "yyyy-MM-dd HH:mm:ss") for t in DefectiveTime]
#             last_time = qt_times[-1]
#             new_time = last_time.addMSecs(900)  
#             qt_times.append(new_time)
#             DefectiveTime = [t.toString("yyyy-MM-dd HH:mm:ss") for t in qt_times]
#         for i in range(len(bad_pos)):
#             # print("TestA")
#             time.sleep(0.1)
#             self.UpdateDefectiveProductHistory(bad_pos[i],DefectiveTime[i])

#         for i in range(len(shortage_pos)):
#             # print("TestB")
#             time.sleep(0.1)
#             self.UpdateShortageProductHistory(int(100-shortage_pos[i]),ShortageTime)
        
#         for f in os.listdir(self.image_directory):
#             if f.endswith('.bmp'):
#                 # os.remove(os.path.join(self.image_directory, f))
#                 #Di chuyển file ảnh đã lưu ở thư mục SourceImages sang thư mục ImagesResult
#                 source_path = os.path.join(self.image_directory, f)  # Đường dẫn tệp gốc
#                 destination_dir = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembleyImage\DataSave"  # Thư mục đích
#                 os.makedirs(destination_dir, exist_ok=True)
#                 shutil.move(source_path, os.path.join(destination_dir, f))
#     #Thực thi nút Reset để xóa trạng thái lable
#     def ResetLable(self):
#         for i in range(1, 101):
#             self.SetStyleSheetLable(f"lbPos{i}", "#A4A4A4")
#         self.parent.lbDefectivetubes.setText("0")
#         self.parent.lbShortagetubes.setText("0")
#         self.parent.lbGeneralImage.setText("Image")
#         self.parent.lbDefectiveImage.setText("Image")
#         print("Reset labels")
#     #Lấy tên sản phẩm từ cơ sở dữ liệu
#     def UpdateDB(self, text):
#         # Cập nhật cơ sở dữ liệu với kết quả kiểm tra
#         c = self.conn.cursor()
#         self.RowId = c.execute("SELECT rowid FROM Product WHERE ProductName = ?", (text,)).fetchall()
#         #Lấy tên file name
#         self.filename = c.execute("SELECT FileName FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         #Lấy chỉ số của BL
#         self.ScoreBL = c.execute("SELECT ScoreBL FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         #Lấy chỉ số của BR
#         self.ScoreBR = c.execute("SELECT ScoreBR FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         #Lấy chỉ số của MID
#         self.ScoreMID = c.execute("SELECT ScoreMID FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         #Lấy chỉ số của TL
#         self.ScoreTL = c.execute("SELECT ScoreTL FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         #Lấy chỉ số của TR
#         self.ScoreTR = c.execute("SELECT ScoreTR FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         print("Tên file:", self.filename[0])
#         print("ScoreBL:", self.ScoreBL[0])
#         print("ScoreBR:", self.ScoreBR[0])
#         print("ScoreMID:", self.ScoreMID[0])
#         print("ScoreTL:", self.ScoreTL[0])
#         print("ScoreTR:", self.ScoreTR[0])

#     def WritePlcVariable(self, address, value1):
#         if PageInitialBackend.PLCConnected:
#             try:
#                 # Ghi một giá trị bit vào PLC
#                 tag = Tag(device=address, value=value1, type=DT.BIT)
#                 self.initial.Plc.write(devices=[tag])
#                 print(f"Đã ghi giá trị {value1} vào {address}")
#             except Exception as e:
#                 print(f"Lỗi khi ghi dữ liệu vào PLC: {e}")
       
#     def WritePlcVariableWord(self, address, value1):
#         if PageInitialBackend.PLCConnected:
#             try:
#                 # Ghi một giá trị word vào PLC
#                 tag = Tag(device=address, value=value1, type=DT.UWORD)
#                 self.initial.Plc.write(devices=[tag])
#                 print(f"Đã ghi giá trị {value1} vào {address}")
#             except Exception as e:
#                 print(f"Lỗi khi ghi dữ liệu vào PLC: {e}")
    
   
#     def ReadD4(self, address):
#         if PageInitialBackend.PLCConnected:
#             try:
#                 # Đọc giá trị từ PLC
#                 tag = Tag(device=address, type=DT.UWORD)
#                 result = self.initial.Plc.read(devices=[tag])
#                 print(f"Đã đọc giá trị {result[0].value} từ {address}")
#             except Exception as e:
#                 print(f"Lỗi khi đọc dữ liệu từ PLC: {e}")
#                 return None
    
#     def initializePage(self):
#         # Trước khi load model mới
#         if torch.cuda.is_available():
#             print("GPUB available")
#             torch.cuda.empty_cache()
#             for attr in ['model', 'Backbone', 'MemoryBL', 'MemoryBR', 'MemoryMID', 'MemoryTL', 'MemoryTR']:
#                 if hasattr(self, attr):
#                     delattr(self, attr)
#         gc.collect()
#         torch.cuda.synchronize()
#         self.image_directory = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceImages" #Nơi chứa ảnh để thực hiện object detection
#         self.prediction = False
#         classes_to_filter = None  # You can give list of classes to filter by name, Be happy you don't have to put class number. ['train','person']
#         self.opt = {
#             "weights": r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\yolov7.torchscript.pt",  # Path to weights file default weights are for nano model
#             "img-size": 576,  # default image size
#             "conf-thres": 0.5,  # confidence threshold for inference.
#             "iou-thres": 0.45,  # NMS IoU threshold for inference.
#             "device": '0' if torch.cuda.is_available() else 'cpu',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
#             "classes": classes_to_filter  # list of classes to filter or None
#         }
#         self.model, self.device, self.half, self.stride, self.imgsz = load_model(self.opt)
#         self.image_paths = [os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
#         self.capture_thread = None
#         self.checking_camera_thread = None 
#         self.checking_plc_thread = None
#         self.Total = 0
#         self.Bad = 0
#         self.Good = 0
#         self.Row = []
#         self.Col = []
#         self.DefectiveTotal = 0
#         self.ShortageTotal = 0
#         self.filename = None
#         self.ScoreBL = 0
#         self.ScoreBR = 0
#         self.ScoreMID = 0
#         self.ScoreTL = 0
#         self.ScoreTR = 0
#         self.failed_labels = []
#         self.error_logs = []
#         #Update Database
#         print("Tên sản phẩm:", self.parent.lbProductName1.text())
#         self.UpdateDB(self.parent.lbProductName1.text())
#         #Tải mô hình anomaly detection
#         if self.filename and self.filename[0]:
#             self.Backbone, self.MemoryBL, self.MemoryBR, self.MemoryMID, self.MemoryTL, self.MemoryTR, self.Transform, self.pca_bl, self.pca_br, self.pca_mid, self.pca_tl, self.pca_tr = self.SetupAnomalyDetection()

#          #Disable các nút ban đầu
#         self.parent.btnReset.setEnabled(False)
#         self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
#         self.parent.btnStop.setEnabled(False)
#         self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
#         self.parent.btnRestart.setEnabled(False)
#         self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
#         self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
#         #Nút nhấn Run và Stop
#         self.Running = False
#         self.blink_count = 0
#         self.blink_colors = ["#DF2026", "#A4A4A4"]  # Đỏ - Xám
#         self.CheckCameraConnectionTimer = QTimer()
#         self.CheckCameraConnectionTimer.timeout.connect(self.CheckCameraConnection)
#         self.CheckCameraConnectionTimer.start(5000)  # Kiểm tra mỗi giây
#         self.CheckPLCConnectionTimer = QTimer()
#         self.CheckPLCConnectionTimer.timeout.connect(self.CheckPLCConnection)
#         self.CheckPLCConnectionTimer.start(5000)  # Kiểm tra mỗi giây
   
#         #Nút nhấn Restart
#         self.btnRestartPressed = False
#         self.btnResetPressed = False 
#         self.parent.lbTubeName.setText(self.parent.label_56.text())
#         #Chạy Trigger
#         self.TriggerPredict = QTimer()
#         self.TriggerPredict.timeout.connect(self.CaptureAndDetect)
#         self.ResetLable()
#         self.parent.btnRun.setEnabled(True)
#         self.SetStyleSheetForbtn("btnRun", "#33D909", "15px")
#         self.parent.lbTotal.setText("0")
#         self.parent.label_204.setText("0")
#         self.parent.label_203.setText("0")
#         self.parent.lbDefectiveTotal.setText("0")
#         self.parent.lbShortageTotal.setText("0")
#         self.parent.lbTimeCounter.setText("0")
#         self.parent.lbTimeDetect.setText("0")
    
#     def UpdateManufactoring(self):
#         if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#             #Lấy dòng database hiện tại trong ProductHistory
#             c = self.conn.cursor()
#             # c.execute("SELECT COUNT(*) FROM ProductHistory")
#             c.execute("SELECT rowid FROM ProductHistory ORDER BY rowid DESC LIMIT 1")
#             # num_rows = c.fetchone()[0]
#             result = c.fetchone()
#             last_rowid = result[0]
#             #Lưu vào database
#             c.execute("UPDATE ProductHistory SET ProductTotal = ?, GoodTotal = ?, BadTotal = ?, DefectiveTotal = ?, ShortageTotal = ? WHERE rowid = ?", (int(self.parent.lbTotal.text()), int(self.parent.label_203.text()),int(self.parent.label_204.text()),int(self.parent.lbDefectiveTotal.text()), int(self.parent.lbShortageTotal.text()), last_rowid))
#             self.conn.commit()

#     def UpdateHistoryTime(self):
#         #Lưu vào database
#         c = self.conn.cursor()
#         c.execute("SELECT rowid FROM ProductHistory ORDER BY rowid DESC LIMIT 1")
#         result = c.fetchone()
#         last_rowid = result[0]
#         c.execute("UPDATE ProductHistory SET EndTime = ? WHERE rowid = ?", (self.End_Time.toString("yyyy-MM-dd hh:mm:ss"), last_rowid))
#         self.conn.commit()

#     def UpdateDefectiveProductHistory(self, error_logs, timestamp):
#         # #Lưu vào database
#         c = self.conn.cursor()
#         c.execute("INSERT INTO ErrorHistory (ErrorName, ProductName, Queue, ErrorPosition, Timestamp) VALUES (?, ?, ?, ?, ?)",
#                 ("Lỗi nắp", self.parent.lbTubeName.text(), (int(self.parent.lbTotal.text()) // 100), error_logs, timestamp))
#         self.conn.commit()
#         print("Inserted new defective error into ErrorHistory.")

#     def UpdateShortageProductHistory(self, error_logs, timestamp):
#         #Lưu vào database
#         c = self.conn.cursor()
#         c.execute("INSERT INTO ErrorHistory (ErrorName, ProductName, Queue, ErrorPosition, Timestamp) VALUES (?, ?, ?, ?, ?)",
#                 ("Lỗi thiếu nắp", self.parent.lbTubeName.text(), (int(self.parent.lbTotal.text()) // 100), error_logs, timestamp))
#         self.conn.commit()
#         print("Inserted new shortage error into ErrorHistory.")
#     #Lưu vào database lỗi camera
#     def UpdateErrorCamera(self, timestamp):
#         #Lưu vào database
#         c = self.conn.cursor()
#         c.execute("INSERT INTO ErrorHistory (ErrorName, ProductName, Timestamp) VALUES (?, ?, ?)",
#                 ("Lỗi kết nối camera", self.parent.lbTubeName.text(), timestamp))
#         self.conn.commit()
#         print("Inserted new camera error into ErrorHistory.")
#     #Lưu vào database lỗi PLC
#     def UpdateErrorPLC(self, timestamp):
#         #Lưu vào database
#         c = self.conn.cursor()
#         c.execute("INSERT INTO ErrorHistory (ErrorName, ProductName, Timestamp) VALUES (?, ?, ?)",
#                 ("Lỗi kết nối PLC", self.parent.lbTubeName.text(), timestamp))
#         self.conn.commit()
#         print("Inserted new PLC error into ErrorHistory.")
        
#     def Push_working_history(self, action_name: str):
#         action_time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
#         c = self.conn.cursor()
#         #Lưu vào database
#         c.execute("INSERT INTO WorkingHistory (FullName, Duty, ActionName, ActionTime) VALUES (?, ?, ?, ?)",
#                 (self.initial.FullName[0], self.initial.Duty[0], action_name, action_time))
        
#         self.conn.commit()
# ########################################################################

from MainUI1 import Ui_MainWindow
from page_Initial import PageInitialBackend
from page_Parameter_ConfimDelay import PageParameterConfirmBackend
from page_Parameter import PageParameterBackend
from PyQt6.QtCore import QTimer, QDateTime
from PyQt6 import QtCore
import os
from CubeDetection import load_model
import torch
import time
from torchvision.transforms import transforms
from torchvision.models import mobilenet_v3_large
from worker_capture import CaptureAndDetectWorker
from CheckingCamera import ConnectionCameraChecker
from CheckingPLC import ConnectionPLCChecker
import re 
from pymelsec.constants import DT
from pymelsec import Type3E
import shutil
from pymelsec.tag import Tag
import gc
import neoapi
import joblib


class DashboardBackend():
    def __init__(self, main: Ui_MainWindow, conn, initial: PageInitialBackend, para: PageParameterBackend, paraconfirm: PageParameterConfirmBackend):
        self.parent = main
        self.conn = conn
        self.initial = initial
        self.para = para
        self.paraconfirm = paraconfirm
        self.paraconfirm.set_confirm_page1(self)
        self.image_directory = r"SourceImages" #Nơi chứa ảnh để thực hiện object detection
        self.prediction = False
        classes_to_filter = None  # You can give list of classes to filter by name, Be happy you don't have to put class number. ['train','person']
        # Trước khi load model mới
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            for attr in ['model', 'Backbone', 'MemoryBL', 'MemoryBR', 'MemoryMID', 'MemoryTL', 'MemoryTR']:
                if hasattr(self, attr):
                    delattr(self, attr)
        gc.collect()
        torch.cuda.synchronize()
        self.opt = {
            "weights": r"yolov7.torchscript.pt",  # Path to weights file default weights are for nano model
            "img-size": 576,  # default image size
            "conf-thres": 0.5,  # confidence threshold for inference.
            "iou-thres": 0.45,  # NMS IoU threshold for inference.
            "device": '0' if torch.cuda.is_available() else 'cpu',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
            "classes": classes_to_filter  # list of classes to filter or None
        }
        self.model, self.device, self.half, self.stride, self.imgsz = load_model(self.opt)
        self.image_paths = [os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        
        self.capture_thread = None
        self.checking_camera_thread = None 
        self.checking_plc_thread = None
        self.Total = 0
        self.Bad = 0
        self.Good = 0
        self.Row = []
        self.Col = []
        self.DefectiveTotal = 0
        self.ShortageTotal = 0
        self.filename = None
        self.ScoreBL = 0
        self.ScoreBR = 0
        self.ScoreMID = 0
        self.ScoreTL = 0
        self.ScoreTR = 0
        self.failed_labels = []
        self.End_Time = None
        self.error = None
        #Update Database
        self.UpdateDB(self.parent.lbProductName1.text())
        #Tải mô hình anomaly detection
        if self.filename and self.filename[0]:
            self.Backbone, self.MemoryBL, self.MemoryBR, self.MemoryMID, self.MemoryTL, self.MemoryTR, self.Transform, self.pca_bl, self.pca_br, self.pca_mid, self.pca_tl, self.pca_tr = self.SetupAnomalyDetection()
        #Disable các nút ban đầu
        self.parent.btnDashboard.setEnabled(True)
        self.parent.btnDashboard1.setEnabled(True)
        self.parent.btnReset.setEnabled(False)
        self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
        self.parent.btnStop.setEnabled(False)
        self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
        self.parent.btnRestart.setEnabled(False)
        self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
        self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
        #Nút nhấn Run và Stop
        self.Running = False
        self.parent.btnRun.clicked.connect(self.RunSystem)
        self.parent.btnStop.clicked.connect(self.StopSystem)
        self.parent.btnLogout.clicked.connect(lambda: [self.StopSystem(), self.Push_working_history("Đăng xuất")])
        #Chớp tắt
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_effect)
        self.blink_count = 0
        self.blink_colors = ["#DF2026", "#A4A4A4"]  # Đỏ - Xám
        #Nút nhấn Restart
        self.btnRestartPressed = False
        self.parent.btnRestart.clicked.connect(lambda: [self.RestartSystem(), self.parent.btnRestart.setEnabled(False), self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px"), self.UpdateSystemStatus()])
        #Nút nhấn Reset
        self.btnResetPressed = False 
        self.parent.btnReset.clicked.connect(lambda: [self.EnableRestart()])
        #Hiển thị tên sản phẩm được chọn từ page Parameter Confirm
        self.parent.lbTubeName.setText(self.parent.label_56.text())      
    #Set style cho label    
    def SetStyleSheetLable(self, object, background_color):
        #Style cho nút btnEmployeeWorking
        button = getattr(self.parent, object)
        button.setStyleSheet(f"""
                QLabel#{object} {{
                    border-radius: 15px;
                    background-color: {background_color};  /* Màu nền mới */
                    color: white;
                    text-align: center;
                    font-family: Inter, sans-serif;
                    border: 1px solid #ffffff;
                }}""")
    #Set style cho nút
    def SetStyleSheetForbtn(self, btn, background_color,pixel):
        #Style cho nút 
        button = getattr(self.parent, btn)
        button.setStyleSheet(f"""
                QPushButton#{btn} {{
                    border-radius: {pixel};
                    border-color: white;
                    background-color: {background_color};  /* Màu nền mới */
                    color: white;
                    text-align: center;
                    font-family: Inter, sans-serif;
                    opacity: 0.7;
                    border: 1px solid #FFFFFF;
                }}

                QPushButton#{btn}:hover {{
                    background-color: #FFA500;  /* Màu nền khi hover */
                }}

                QPushButton#{btn}:pressed {{
                    padding-left: 5px;
                    padding-top: 5px;
                }}
                """)
    #Chạy hệ thống
    def RunSystem(self):
        self.Push_working_history("Bắt đầu hệ thống")
        self.SetStyleSheetLable("lbStatusSystem", "#33D909")
        # self.parent.lbStatusSystem.setText("ONLINE")
        self.parent.btnRun.setEnabled(False)
        self.SetStyleSheetForbtn("btnRun", "#A4A4A4", "15px")
        self.parent.btnStop.setEnabled(True)
        self.SetStyleSheetForbtn("btnStop", "#F23030", "15px")
        self.ResetLable()

        self.capture_thread = CaptureAndDetectWorker(self, self.initial, self.parent,self.paraconfirm, self.model, 
                                                    self.device, 
                                                    self.half, 
                                                    self.stride, 
                                                    self.imgsz, 
                                                    self.opt, 
                                                    self.image_directory
                                                    )
        self.capture_thread.finished.connect(self.onCaptureFinished)
        #Mô phỏng
        self.capture_thread.start()
    #Dừng hệ thống
    def StopSystem(self):
        self.Push_working_history("Dừng hệ thống")
        self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
        self.parent.btnRun.setEnabled(True)
        self.SetStyleSheetForbtn("btnRun", "#33D909", "15px")
        self.parent.btnStop.setEnabled(False)
        self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
        self.End_Time = QtCore.QDateTime.currentDateTime()
        print("Time_Start: ", self.End_Time.toString("yyyy-MM-dd hh:mm:ss"))
        self.UpdateHistoryTime()
    #Kết nối PLC
    def PLCConnection(self,plc_host, plc_port, plc_type):
        print("Checking PLC connection...")
        print("PageInitialBackend.PLCConnected:", PageInitialBackend.PLCConnected)
        if PageInitialBackend.PLCConnected:
            return True
        try:
            PageInitialBackend.Plc = Type3E(host=plc_host, port=plc_port, plc_type=plc_type)
            PageInitialBackend.Plc.set_access_opt(comm_type='binary')
            PageInitialBackend.Plc.connect(ip=plc_host, port=plc_port)
            # self.plc_time = PageInitialBackend.Plc.read_plc_time()
            print("Connecting to PLC.")
            PageInitialBackend.PLCConnected = True
            # self.CheckPLCConnectionTimer.start(5000)
        except Exception as e:
            print(f"Error connecting to PLC: {e}")
            PageInitialBackend.PLCConnected = False
            return False
    #Kết nối camera
    def CameraConnection(self):
        # Kiểm tra xem camera đã kết nối hay chưa
        print("Checking camera connection...")
        print("PageInitialBackend.CameraConnected:", PageInitialBackend.CameraConnected)
        if PageInitialBackend.CameraConnected:
            return True
        try:
            PageInitialBackend.Camera = neoapi.Cam()
            PageInitialBackend.Camera.Connect()   
            PageInitialBackend.CameraName = PageInitialBackend.Camera.GetFeature("DeviceModelName").GetString()
            print(f"Camera connected: {PageInitialBackend.CameraName}")
            if PageInitialBackend.Camera.IsConnected():
                print("Connecting to Camera.")
                PageInitialBackend.CameraConnected = True
                return True
            else:
                PageInitialBackend.CameraConnected = False
                raise Exception("Camera not connected.")
        except (neoapi.NeoException, Exception) as e:
            print(f"Error checking camera connection1: {e}")
            PageInitialBackend.CameraConnected = False
            return False
    #Kiểm tra kết nối camera
    def CheckCameraConnection(self):
        self.checking_camera_thread = ConnectionCameraChecker(self.initial.CheckCameraConnection)
        self.checking_camera_thread.finished.connect(self.onCameraConnectionChecked)
        self.checking_camera_thread.start()
        if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
            self.parent.btnRestart.setEnabled(False)
            self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
            self.parent.btnReset.setEnabled(False)
            self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
    #Kiểm tra kết nối PLC
    def CheckPLCConnection(self):
        self.checking_plc_thread = ConnectionPLCChecker(self.initial.CheckPLCConnection)
        self.checking_plc_thread.finished.connect(self.onPLCConnectionChecked)
        self.checking_plc_thread.start()
        if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
            self.parent.btnRestart.setEnabled(False)
            self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
            self.parent.btnReset.setEnabled(False)
            self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
    #Kiểm tra kết nối hệ thống
    def CheckSystemConnection(self):
        if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
            self.parent.btnRestart.setEnabled(False)
            self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
            self.parent.btnReset.setEnabled(False)
            self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
            self.SetStyleSheetLable("lbCameraConnected", "#33D909")
            self.SetStyleSheetLable("lbPLCConnected", "#33D909")
    #Thực thi kiểm tra kết nối camera
    def onCameraConnectionChecked(self, result):
        if result:
            self.SetStyleSheetLable("lbCameraConnected", "#33D909")
        else:
            self.failed_labels.append("lbCameraConnected")
            self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
            self.parent.btnRun.setEnabled(False)
            self.SetStyleSheetForbtn("btnRun", "#A4A4A4", "15px")
            self.parent.btnStop.setEnabled(False)
            self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
            self.parent.btnReset.setEnabled(True)
            self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
            self.Error_Camera_Time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            self.UpdateErrorCamera(self.Error_Camera_Time)
            if self.failed_labels:
                self.blink_count = 0
                self.blink_timer.start(500)
                self.parent.btnReset.setEnabled(True)
                self.SetStyleSheetForbtn("btnReset", "#FFDE21", "15px")
    #Thực thi kiểm tra kết nối PLC
    def onPLCConnectionChecked(self, result):
        self.ReadD4("D4")
        if result:
            self.SetStyleSheetLable("lbPLCConnected", "#33D909")
        else:
            PageInitialBackend.Plc.close()
            self.checking_plc_thread.exit()
            self.checking_plc_thread.wait()
            self.TriggerPredict.stop()
            self.failed_labels.append("lbPLCConnected")
            self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
            self.parent.btnRun.setEnabled(False)
            self.SetStyleSheetForbtn("btnRun", "#A4A4A4", "15px")
            self.parent.btnStop.setEnabled(False)
            self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
            self.parent.btnReset.setEnabled(True)
            self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
            self.Error_PLC_Time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            self.UpdateErrorPLC(self.Error_PLC_Time)
            if self.failed_labels:
                self.blink_count = 0
                self.blink_timer.start(500)
                self.parent.btnReset.setEnabled(True)
                self.SetStyleSheetForbtn("btnReset", "#FFDE21", "15px")
    #Nhấp nháy đèn báo lỗi
    def blink_effect(self):
        color = self.blink_colors[self.blink_count % 2]  # Chọn màu
        for label in self.failed_labels:
            self.SetStyleSheetLable(label, color)

        self.blink_count += 1
    #Restart hệ thống - Khởi động lại hệ thống
    def RestartSystem(self):
        self.Push_working_history("Nhấn nút khởi động lại hệ thống")
        self.failed_labels = []
        self.btnRestartPressed = True
        #Thực tế
        self.PLCConnection(self.parent.leditPLCHost.text(), int(self.parent.leditPLCPort.text()), self.parent.leditPLCType.text())
        self.CameraConnection()
        print("PLC Connected1:", PageInitialBackend.PLCConnected)
        print("Camera Connected1:", PageInitialBackend.CameraConnected)
        if PageInitialBackend.PLCConnected:
            self.SetStyleSheetLable("lbPLCConnected", "#33D909")
        else:
            self.failed_labels.append("lbPLCConnected")

        if PageInitialBackend.CameraConnected:
            self.SetStyleSheetLable("lbCameraConnected", "#33D909")
        else:
            self.failed_labels.append("lbCameraConnected")
        if self.failed_labels:
            self.blink_timer.start(500)
            self.parent.btnReset.setEnabled(True)
            self.SetStyleSheetForbtn("btnReset", "#FFDE21", "15px")
        if (not PageInitialBackend.PLCConnected or not PageInitialBackend.CameraConnected) and self.btnRestartPressed:
            self.parent.btnReset.setEnabled(True)
            self.SetStyleSheetForbtn("btnReset", "#FFDE21", "15px")
        else:
            self.parent.btnRun.setEnabled(True)
            self.SetStyleSheetForbtn("btnRun", "#33D909", "15px")
            self.parent.btnRestart.setEnabled(False)
            self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
    #Cho phép nhấn nút tắt đèn cảnh báo
    def EnableRestart(self):
        self.Push_working_history("Nhấn nút tắt đèn cảnh báo")
        self.btnResetPressed = True
        if (not PageInitialBackend.PLCConnected or not PageInitialBackend.CameraConnected) and self.btnResetPressed:
            self.parent.btnRestart.setEnabled(True)
            self.SetStyleSheetForbtn("btnRestart", "#F68013", "15px")
            self.CheckCameraConnectionTimer.stop()  # Dừng kiểm tra kết nối khi nhấn Reset
            self.CheckPLCConnectionTimer.stop()  # Dừng kiểm tra kết nối khi nhấn Reset
            self.parent.btnReset.setEnabled(False)  # Ẩn nút Reset sau khi nhấn
            self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
            self.blink_timer.stop()
            for label in self.failed_labels:
                self.SetStyleSheetLable(label, "#A4A4A4")  # Đổi về màu xám
            self.failed_labels.clear()  # Xóa danh sách lỗi
        else: 
            #Tắt đèn tháp và xy lanh (làm sau)
            #Tắt nút btnReset
            self.parent.btnReset.setEnabled(False)  # Ẩn nút Reset sau khi nhấn
            self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")

    #Update trạng thái hệ thống ở trang Initial
    def UpdateSystemStatus(self):
        if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
            self.parent.btnSystemConnection.setEnabled(False)
            self.parent.btnSystemConnection.setText("Đã kết nối")
            self.initial.SetStyleSheetLable("lbPLCConnected_2", "#33D909")
            self.initial.SetStyleSheetLable("lbCameraConnected_2", "#33D909")
        elif PageInitialBackend.PLCConnected and not PageInitialBackend.CameraConnected:
            self.parent.btnSystemConnection.setEnabled(True)
            self.parent.btnSystemConnection.setText("Kết nối hệ thống")
        elif not PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
            self.parent.btnSystemConnection.setEnabled(True)
            self.parent.btnSystemConnection.setText("Kết nối hệ thống")
    #Lấy tên tệp hình ảnh tiếp theo
    def GetNextFilename(self):
        # Kiểm tra thư mục tồn tại
        if not os.path.exists(self.image_directory):
            print(f"Directory not found, creating: {self.image_directory}")
            os.makedirs(self.image_directory)  # Tạo thư mục nếu không tồn tại

        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("yyyy-MM-dd-hh-mm-ss")
        filename = f"{formatted_datetime}_IMG.bmp"
        file_path = os.path.join(self.image_directory, filename)

        return file_path

    #Thực hiện lấy ảnh từ camera và làm object detection
    def CaptureAndDetect(self):
        if PageInitialBackend.CameraConnected and PageInitialBackend.PLCConnected:
            self.paraconfirm.GetPlcVariableForTrigger()
            # print("Waiting for next trigger")
            if self.paraconfirm.triggered:
                self.paraconfirm.processing = True
                print("Trigger activated, processing images...")
                self.ResetLable()
                try:
                    time.sleep(self.paraconfirm.Delay[0])
                    if self.para.trigger:
                            self.para.trigger.Execute()
                    else:
                        print("Trigger is not initialized.")
                    # FLUSH buffer để bỏ ảnh cũ, nếu có
                    while True:
                        old = PageInitialBackend.Camera.GetImage(timeout=100)
                        if old is None:
                            break
            
                    img_camera = PageInitialBackend.Camera.GetImage(timeout=1000)
                    if img_camera is None:
                        print("Failed to capture image from camera.")
                    else:
                        print("Image captured successfully.")

                        file_path = self.GetNextFilename()
                        img_camera.Save(file_path)
                        self.capture_thread.start()
                except Exception as e:
                    print(f"Error capturing or saving image: {e}")
                finally:
                    self.paraconfirm.triggered = False  # Đặt lại trigger để chờ lần kích hoạt tiếp theo
                    self.paraconfirm.processing = False
            else: 
                self.capture_thread.exit()
                self.capture_thread.wait()
        else:
            print("Camera or PLC is not connected.")  
   
    #Tải mô hình phát hiện bất thường
    def SetupAnomalyDetection(self):
        print("Setting up anomaly detection...")
        Transform = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor()])
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
        Backbone = mobilenet_feature_extractor().cuda()
        # Kiểm tra nếu truy vấn trả về kết quả hợp lệ
        if self.filename and self.filename[0]: 
            print("Filename:", self.filename[0])         
            # Tìm màu bằng regex (màu là phần đầu tiên trước từ "PLASTIC")
            match = re.match(r"([A-Z]+)PLASTIC", self.filename[0])
            if match:
                color = match.group(1).lower()  # Lấy màu và chuyển thành chữ thường
                
                # Định nghĩa các vị trí model cần tải
                positions = ["bl", "br", "mid", "tl", "tr"]

                # Tạo và tải model động
                base_path = rf"H:\HK242\LVTN\Model\{self.filename[0]}\memory_bank_{color}_"
                base_path_pca = rf"H:\HK242\LVTN\Model\{self.filename[0]}\pca_{color}_"
                models = {}
                models_pca = {}
                try:
                    for pos in positions:
                        model_path = base_path + f"{pos}_final.pt"
                        model_path_pca = base_path_pca + f"{pos}.pkl"
                        # model_path = base_path + f"{pos}_pca.pt"
                        models[pos.upper()] = torch.load(model_path).cuda()
                        models_pca[pos.upper()] = joblib.load(model_path_pca)
                        #Hiển thị shape của model
                        print(f"Model {pos.upper()} shape:", models[pos.upper()].shape)
                    # Giải nén dictionary vào các biến MemoryBL, MemoryBR...
                    MemoryBL, MemoryBR, MemoryMID, MemoryTL, MemoryTR = (
                        models["BL"], models["BR"], models["MID"], models["TL"], models["TR"]
                    )
                    # Giải nén dictionary vào các biến pca_bl, pca_br...
                    pca_bl, pca_br, pca_mid, pca_tl, pca_tr = (
                        models_pca["BL"], models_pca["BR"], models_pca["MID"], models_pca["TL"], models_pca["TR"]
                    )
                except FileNotFoundError as e:
                    print(f"Lỗi: Không tìm thấy model {model_path} - {e}")
            else:
                print(f"Lỗi: Không tìm thấy màu trong '{self.filename}'!")
        else:
            print("Lỗi: Không lấy được tên file từ database!")
        return Backbone, MemoryBL, MemoryBR, MemoryMID, MemoryTL, MemoryTR, Transform, pca_bl, pca_br, pca_mid, pca_tl, pca_tr
    #Thực thi điều chỉnh UI khi hoàn tất 
    def onCaptureFinished(self, bad_pos, shortage_pos, DefectiveTime, ShortageTime):
        #Kiểm tra trong 100 ô có ô nào màu xám nữa không
        gray_color = "#A4A4A4"
        found_labels = []
        for i in range(1, 101):
            label_name = f"lbPos{i}"
            label = getattr(self.parent, label_name, None)
            if label:
                current_style = label.styleSheet()
                if gray_color.lower() in current_style.lower():
                    found_labels.append(label_name)
        # Đặt màu theo điều kiện số lượng label
        new_color = "#F68013" if len(found_labels) > 50 else "#33D909"
        # Cập nhật màu cho các label tìm được
        for label_name in found_labels:
            self.SetStyleSheetLable(label_name, new_color)
        print("Bad positions:", bad_pos)
        print("Shortage positions:", shortage_pos)
        print("DefectiveTime:", DefectiveTime)
        print("ShortageTime:", ShortageTime)
        self.DefectiveTotal += len(bad_pos) 
        self.ShortageTotal += len(shortage_pos)
        self.parent.lbDefectiveTotal.setText(str(self.DefectiveTotal))
        self.parent.lbShortageTotal.setText(str(self.ShortageTotal))
        self.Bad += len(bad_pos) + len(shortage_pos)
        self.Good = self.Total - self.Bad
        self.parent.label_204.setText(str(self.Bad))
        self.parent.label_203.setText(str(self.Good))
        #Xóa file ảnh đã lưu ở thư mục SourceImages
        for f in os.listdir(self.image_directory):
            if f.endswith('.bmp'):
                # os.remove(os.path.join(self.image_directory, f))
                #Di chuyển file ảnh đã lưu ở thư mục SourceImages sang thư mục ImagesResult
                source_path = os.path.join(self.image_directory, f)  # Đường dẫn tệp gốc
                destination_dir = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembleyImage\DataSave"  # Thư mục đích
                os.makedirs(destination_dir, exist_ok=True)
                shutil.move(source_path, os.path.join(destination_dir, f))

        while len(bad_pos) > len(DefectiveTime):
            qt_times = [QtCore.QDateTime.fromString(t, "yyyy-MM-dd HH:mm:ss") for t in DefectiveTime]
            last_time = qt_times[-1]
            new_time = last_time.addMSecs(900)  
            qt_times.append(new_time)
            DefectiveTime = [t.toString("yyyy-MM-dd HH:mm:ss") for t in qt_times]
        for i in range(len(bad_pos)):
            # print("TestA")
            time.sleep(0.1)
            self.UpdateDefectiveProductHistory(bad_pos[i],DefectiveTime[i])

        for i in range(len(shortage_pos)):
            # print("TestB")
            time.sleep(0.1)
            self.UpdateShortageProductHistory(int(100-shortage_pos[i]),ShortageTime)
            
    #Thực thi nút Reset để xóa trạng thái lable
    def ResetLable(self):
        for i in range(1, 101):
            self.SetStyleSheetLable(f"lbPos{i}", "#A4A4A4")
        self.parent.lbDefectivetubes.setText("0")
        self.parent.lbShortagetubes.setText("0")
        self.parent.lbGeneralImage.setText("Image")
        self.parent.lbDefectiveImage.setText("Image")
        print("Reset labels")
    #Lấy tên sản phẩm từ cơ sở dữ liệu
    def UpdateDB(self, text):
        # Cập nhật cơ sở dữ liệu với kết quả kiểm tra
        c = self.conn.cursor()
        self.RowId = c.execute("SELECT rowid FROM Product WHERE ProductName = ?", (text,)).fetchall()
        #Lấy tên file name
        self.filename = c.execute("SELECT FileName FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        #Lấy chỉ số của BL
        self.ScoreBL = c.execute("SELECT ScoreBL FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        #Lấy chỉ số của BR
        self.ScoreBR = c.execute("SELECT ScoreBR FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        #Lấy chỉ số của MID
        self.ScoreMID = c.execute("SELECT ScoreMID FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        #Lấy chỉ số của TL
        self.ScoreTL = c.execute("SELECT ScoreTL FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        #Lấy chỉ số của TR
        self.ScoreTR = c.execute("SELECT ScoreTR FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        print("Tên file:", self.filename[0])
        print("ScoreBL:", self.ScoreBL[0])
        print("ScoreBR:", self.ScoreBR[0])
        print("ScoreMID:", self.ScoreMID[0])
        print("ScoreTL:", self.ScoreTL[0])
        print("ScoreTR:", self.ScoreTR[0])

    def WritePlcVariableWord(self, address, value1):
        if PageInitialBackend.PLCConnected:
            try:
                # Ghi một giá trị word vào PLC
                tag = Tag(device=address, value=value1, type=DT.UWORD)
                self.initial.Plc.write(devices=[tag])
                print(f"Đã ghi giá trị {value1} vào {address}")
            except Exception as e:
                print(f"Lỗi khi ghi dữ liệu vào PLC: {e}")
    
    def ReadD4(self, address):
        if PageInitialBackend.PLCConnected:
            try:
                # Đọc giá trị từ PLC
                tag = Tag(device=address, type=DT.UWORD)
                result = self.initial.Plc.read(devices=[tag])
                print(f"Đã đọc giá trị {result[0].value} từ {address}")
            except Exception as e:
                print(f"Lỗi khi đọc dữ liệu từ PLC: {e}")
                return None
    
    def UpdateManufactoring(self):
        if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
            #Lấy dòng database hiện tại trong ProductHistory
            c = self.conn.cursor()
            c.execute("SELECT COUNT(*) FROM ProductHistory")
            num_rows = c.fetchone()[0]
            c.execute("UPDATE ProductHistory SET ProductTotal = ?, GoodTotal = ?, BadTotal = ?, DefectiveTotal = ?, ShortageTotal = ? WHERE rowid = ?", (int(self.parent.lbTotal.text()), int(self.parent.label_203.text()),int(self.parent.label_204.text()),int(self.parent.lbDefectiveTotal.text()), int(self.parent.lbShortageTotal.text()), num_rows))
            self.conn.commit()

    def UpdateHistoryTime(self):
        #Lưu vào database
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM ProductHistory")
        num_rows = c.fetchone()[0]
        c.execute("UPDATE ProductHistory SET EndTime = ? WHERE rowid = ?", (self.End_Time.toString("yyyy-MM-dd hh:mm:ss"), num_rows))
        self.conn.commit()

    def UpdateDefectiveProductHistory(self, error_logs, timestamp):
        # #Lưu vào database
        c = self.conn.cursor()
        c.execute("INSERT INTO ErrorHistory (ErrorName, ProductName, Queue, ErrorPosition, Timestamp) VALUES (?, ?, ?, ?, ?)",
                ("Lỗi nắp", self.parent.lbTubeName.text(), (int(self.parent.lbTotal.text()) // 100), error_logs, timestamp))
        self.conn.commit()
        print("Inserted new defective error into ErrorHistory.")

    def UpdateShortageProductHistory(self, error_logs, timestamp):
        #Lưu vào database
        c = self.conn.cursor()
        c.execute("INSERT INTO ErrorHistory (ErrorName, ProductName, Queue, ErrorPosition, Timestamp) VALUES (?, ?, ?, ?, ?)",
                ("Lỗi thiếu nắp", self.parent.lbTubeName.text(), (int(self.parent.lbTotal.text()) // 100), error_logs, timestamp))
        self.conn.commit()
        print("Inserted new shortage error into ErrorHistory.")
    #Lưu vào database lỗi camera
    def UpdateErrorCamera(self, timestamp):
        #Lưu vào database
        c = self.conn.cursor()
        c.execute("INSERT INTO ErrorHistory (ErrorName, ProductName, Timestamp) VALUES (?, ?, ?,)",
                ("Lỗi kết nối camera", self.parent.lbTubeName.text(), timestamp))
        self.conn.commit()
        print("Inserted new camera error into ErrorHistory.")
    #Lưu vào database lỗi PLC
    def UpdateErrorPLC(self, timestamp):
        #Lưu vào database
        c = self.conn.cursor()
        c.execute("INSERT INTO ErrorHistory (ErrorName, ProductName, Timestamp) VALUES (?, ?, ?)",
                ("Lỗi kết nối PLC", self.parent.lbTubeName.text(), timestamp))
        self.conn.commit()
        print("Inserted new PLC error into ErrorHistory.")
        
    def initializePage(self):
        # Trước khi load model mới
        if torch.cuda.is_available():
            print("GPUB available")
            torch.cuda.empty_cache()
            for attr in ['model', 'Backbone', 'MemoryBL', 'MemoryBR', 'MemoryMID', 'MemoryTL', 'MemoryTR']:
                if hasattr(self, attr):
                    delattr(self, attr)
        gc.collect()
        torch.cuda.synchronize()
        self.image_directory = r"SourceImages" #Nơi chứa ảnh để thực hiện object detection
        self.prediction = False
        classes_to_filter = None  # You can give list of classes to filter by name, Be happy you don't have to put class number. ['train','person']
        self.opt = {
            "weights": r"yolov7.torchscript.pt",  # Path to weights file default weights are for nano model
            "img-size": 576,  # default image size
            "conf-thres": 0.5,  # confidence threshold for inference.
            "iou-thres": 0.45,  # NMS IoU threshold for inference.
            "device": '0' if torch.cuda.is_available() else 'cpu',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
            "classes": classes_to_filter  # list of classes to filter or None
        }
        self.model, self.device, self.half, self.stride, self.imgsz = load_model(self.opt)
        self.image_paths = [os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        self.capture_thread = None
        self.checking_camera_thread = None 
        self.checking_plc_thread = None
        self.Total = 0
        self.Bad = 0
        self.Good = 0
        self.Row = []
        self.Col = []
        self.DefectiveTotal = 0
        self.ShortageTotal = 0
        self.filename = None
        self.ScoreBL = 0
        self.ScoreBR = 0
        self.ScoreMID = 0
        self.ScoreTL = 0
        self.ScoreTR = 0
        self.failed_labels = []
        self.error_logs = []
        #Update Database
        print("Tên sản phẩm:", self.parent.lbProductName1.text())
        self.UpdateDB(self.parent.lbProductName1.text())
        #Tải mô hình anomaly detection
        if self.filename and self.filename[0]:
            self.Backbone, self.MemoryBL, self.MemoryBR, self.MemoryMID, self.MemoryTL, self.MemoryTR, self.Transform, self.pca_bl, self.pca_br, self.pca_mid, self.pca_tl, self.pca_tr = self.SetupAnomalyDetection()
         #Disable các nút ban đầu
        self.parent.btnReset.setEnabled(False)
        self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")
        self.parent.btnStop.setEnabled(False)
        self.SetStyleSheetForbtn("btnStop", "#A4A4A4", "15px")
        self.parent.btnRestart.setEnabled(False)
        self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
        self.SetStyleSheetLable("lbStatusSystem", "#A4A4A4")
        #Nút nhấn Run và Stop
        self.Running = False
        self.blink_count = 0
        self.blink_colors = ["#DF2026", "#A4A4A4"]  # Đỏ - Xám
        #Nút nhấn Restart
        self.btnRestartPressed = False
        self.btnResetPressed = False 
        self.parent.lbTubeName.setText(self.parent.label_56.text())
        self.ResetLable()
        self.parent.btnRun.setEnabled(True)
        self.SetStyleSheetForbtn("btnRun", "#33D909", "15px")
        self.parent.lbTotal.setText("0")
        self.parent.label_204.setText("0")
        self.parent.label_203.setText("0")
        self.parent.lbDefectiveTotal.setText("0")
        self.parent.lbShortageTotal.setText("0")
        self.parent.lbTimeCounter.setText("0")
        self.parent.lbTimeDetect.setText("0")

    def Push_working_history(self, action_name: str):
        action_time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        c = self.conn.cursor()
        #Lưu vào database
        c.execute("INSERT INTO WorkingHistory (FullName, Duty, ActionName, ActionTime) VALUES (?, ?, ?, ?)",
                (self.initial.FullName[0], self.initial.Duty[0], action_name, action_time))
        self.conn.commit()
