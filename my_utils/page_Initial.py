from MainUI1 import Ui_MainWindow
from PyQt6 import QtCore
import pandas as pd
from pymelsec import Type3E
from pymelsec.constants import DT
import neoapi
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
import sys
from CheckingCamera import ConnectionCameraChecker
from CheckingPLC import ConnectionPLCChecker
from cryptography.fernet import Fernet
from pymelsec.tag import Tag
#------------------------------------------------------------------------------------
# class PageInitialBackend:
#     CameraConnected = False
#     Camera = None
#     PLCConnected = False
#     Plc = None
#     FailedLabels = []
#     CameraName = None
#     ConnectionMonitorTimer = None
#     def __init__(self, main: Ui_MainWindow, conn, KeyPrimary):
#         #Thiết lập biến
#         self.parent = main
#         self.conn = conn
#         self.KeyPrimary = KeyPrimary
#         #Thiết lập giao diện
#         self.parent.btnDashboard.setEnabled(False)
#         self.parent.btnDashboard1.setEnabled(False)
#         self.parent.btnParameter.setEnabled(False)
#         self.parent.btnParameter1.setEnabled(False)
#         #Kiểm tra kết nối DB
#         if self.conn is None:
#             raise Exception("Database connection is not available!")
#         #Đọc file csv chứa thông tin input từ máy
#         self.uri_machine_input_value = pd.read_csv(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\Document\no_rub_input_value.csv", index_col=0)
#         self.dinput_addr = [*self.uri_machine_input_value['ID_Input']]
#         self.dinput_type = [*self.uri_machine_input_value['Input_Type']]
#         self.dinput_name = [name.strip() for name in [*self.uri_machine_input_value['Input_Name']]]
#         self.dinput_index = [*self.uri_machine_input_value['Input_Index']]
#         self.dinput_lenght = len(self.dinput_addr)
#         self.dinput_old = [-1]*self.dinput_lenght
#         #Liên kết dữ liệu từ DB
#         self.ImportDataFromDB()
#         #Ghi log
#         self.Push_working_history("Đăng nhập vào hệ thống")
#         # Xác nhận vị trí 
#         self.parent.btnConfirm.setEnabled(False)
#         self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
#         self.parent.btnConfirm.clicked.connect(lambda:[self.parent.stackedWidget.setCurrentWidget(self.parent.page_Parameter), self.ToggleMenu(), self.StopVideo(), self.Push_working_history("Xác nhận vị trí camera")])
#         # self.parent.btnConfirm.clicked.connect(lambda:[self.parent.stackedWidget.setCurrentWidget(self.parent.page_Parameter), self.ToggleMenu()])
#         self.parent.btnInitial.clicked.connect(lambda:[self.VideoTimer.start(30)])
#         self.parent.btnInitial1.clicked.connect(lambda:[self.VideoTimer.start(30)])
#         self.error_logs = []
#         self.plc_time = None
#         self.checking_camera_thread = None
#         self.checking_plc_thread = None
#         self.count_error_camera = 0
#         self.count_error_plc = 0
        
#         # Hiệu ứng nhấp nháy
#         self.blink_timer = QTimer()
#         self.blink_timer.timeout.connect(self.blink_effect)
#         self.blink_count = 0
#         self.blink_time = 6  # 6 lần (3 giây, mỗi 0.5s)
#         self.blink_colors = ["#DF2026", "#A4A4A4"]  # Đỏ - Xám
#         # Ngắt kết nối trước khi kết nối lại
#         if self.parent.btnSystemConnection.receivers(self.parent.btnSystemConnection.clicked) > 0:
#             self.parent.btnSystemConnection.clicked.disconnect()
#         #Kết nối hệ thống
#         self.parent.btnSystemConnection.clicked.connect(lambda: [self.handleSystemConnection(), self.HandleBtnSystemConnection(), self.Push_working_history("Kết nối hệ thống")])
        
#         #Thay đổi cấu hình PLC
#         self.ModifyEmployee(False)
#         self.SetStyleSheetForbtn("btnSavePLC", "#A4A4A4")
#         self.parent.btnModifyPLC.clicked.connect(lambda: [self.ModifyEmployee(True),self.SetStyleSheetForbtn("btnSavePLC", "#DF2026"),self.parent.btnModifyPLC.setEnabled(False),self.SetStyleSheetForbtn("btnModifyPLC", "#A4A4A4"), self.Push_working_history("Thay đổi cấu hình PLC")])
#         self.parent.btnSavePLC.clicked.connect(lambda:[self.ModifyDataDB(),self.ModifyEmployee(False),self.SetStyleSheetForbtn("btnSavePLC","#A4A4A4"),self.parent.btnModifyPLC.setEnabled(True),self.SetStyleSheetForbtn("btnModifyPLC", "#F68013"), self.Push_working_history("Lưu cấu hình PLC")])
#         #Check System Connection, 3 giây kiểm tra 1 lần - Kiểm tra thực tế
#         PageInitialBackend.ConnectionMonitorTimer = QTimer()
#         PageInitialBackend.ConnectionMonitorTimer.timeout.connect(self.ConnectionMonitor)
#         self.CheckCameraConnection1timer = QTimer()
#         self.CheckCameraConnection1timer.timeout.connect(self.CheckCameraConnection1)
#         self.CheckPLCConnection1timer = QTimer()
#         self.CheckPLCConnection1timer.timeout.connect(self.CheckPLCConnection1)
        
#     #Thiết lập bar side cho giao diện    
#     def ToggleMenu(self):
#         if self.parent.widgetOpen.isHidden():
#             self.parent.stackedWidget.setMinimumSize(QtCore.QSize(1415, 789))
#             self.parent.stackedWidget.setMaximumSize(QtCore.QSize(1415, 789))
#         elif self.parent.widgetClose.isHidden():
#             self.parent.stackedWidget.setMinimumSize(QtCore.QSize(1325, 789))
#             self.parent.stackedWidget.setMaximumSize(QtCore.QSize(1325, 789))
#     #Kết nối PLC
#     def PLCConnection(self,plc_host, plc_port, plc_type):
#         print("Checking PLC connection...")
#         if PageInitialBackend.PLCConnected:
#             return True
#         try:
#             PageInitialBackend.Plc = Type3E(host=plc_host, port=plc_port, plc_type=plc_type)
#             PageInitialBackend.Plc.set_access_opt(comm_type='binary')
#             PageInitialBackend.Plc.connect(ip=plc_host, port=plc_port)
#             # self.plc_time = PageInitialBackend.Plc.read_plc_time()
#             print("Connecting to PLC.")
#             PageInitialBackend.PLCConnected = True
#             # self.WritePlcVariable("M4022", 1)
#             self.CheckPLCConnection1timer.start(5000)
#         except Exception as e:
#             print(f"Error connecting to PLC: {e}")
#             PageInitialBackend.PLCConnected = False
#             return False    
#         else:
#             print("PLC connection lost.")
#     #Kiểm tra kết nối PLC
#     def CheckPLCConnection(self):
#         if PageInitialBackend.PLCConnected:
#             try:
#                 # Đọc một biến trạng thái từ PLC để kiểm tra kết nối
#                 read_result = PageInitialBackend.Plc.batch_read(ref_device='SM400',
#                                                     read_size=1, 
#                                                     data_type=DT.BIT)
#                 PageInitialBackend.PLCConnected = True      
#                 print("PLC connection is active.")
#                 return True    
#             except Exception:
#                 print("PLC connection lost.1")
#                 PageInitialBackend.PLCConnected = False  # mất kết nối
#                 return False
#     #Kết nối camera
#     def CameraConnection(self):
#         # Kiểm tra xem camera đã kết nối hay chưa
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
#                 self.CheckCameraConnection1timer.start(5000)
#                 return True
#             else:
#                 PageInitialBackend.CameraConnected = False
#                 raise Exception("Camera not connected.")
#         except (neoapi.NeoException, Exception) as e:
#             print(f"Error checking camera connection1: {e}")
#             #error_logs.append(str(e))
#             PageInitialBackend.CameraConnected = False
#             return False
#     #Kết nối PLC và Camera
#     def SystemConnection(self):
#         self.CameraConnection()
#         self.PLCConnection(self.parent.leditPLCHost.text(), int(self.parent.leditPLCPort.text()), self.parent.leditPLCType.text())
#         self.Error_Camera_Time = 0
#         self.Error_PLC_Time = 0
#         if PageInitialBackend.PLCConnected:
#             self.SetStyleSheetLable("lbPLCConnected_2", "#33D909")
#         else:
#             PageInitialBackend.FailedLabels.append("lbPLCConnected_2")

#         if PageInitialBackend.CameraConnected:
#             self.SetStyleSheetLable("lbCameraConnected_2", "#33D909")
#         else:
#             PageInitialBackend.FailedLabels.append("lbCameraConnected_2")

#          # Nếu có lỗi, bắt đầu nhấp nháy
#         if PageInitialBackend.FailedLabels:
#             self.blink_count = 0
#             self.blink_timer.start(500)  # Mỗi 0.5 giây
#             QTimer.singleShot(3000, self.reset_connection_status)  # Sau 3 giây reset

#         #if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#         if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#             PageInitialBackend.ConnectionMonitorTimer.start(1000)
#             # self.CheckCameraConnection1timer.start(5000)
#             # self.CheckPLCConnection1timer.start(5000)
#             print("System Connection")
#             self.parent.btnSystemConnection.setEnabled(False)
#             self.parent.btnSystemConnection.setText("Đã kết nối")
#             # self.ShowVideo()
#             self.AllowChangePage()
#             return True
#         else:
#             self.parent.btnSystemConnection.setEnabled(False)
#             self.parent.btnSystemConnection.setText("Đang kết nối")
#     #Set style cho lable
#     def SetStyleSheetLable(self, object, background_color):
#         #Style cho nút btnEmployeeWorking
#         button = getattr(self.parent, object)
#         button.setStyleSheet(f"""
#                 QLabel#{object} {{
#                     border-radius: 15px;
#                     border-color: white;
#                     background-color: {background_color};  /* Màu nền mới */
#                     color: white;
#                     text-align: center;
#                     font-family: Inter, sans-serif;
#                 }}""")
#     #Cho phép điều chỉnh cấu hình PLC
#     def ModifyEmployee(self,command):
#         #Cho phép điều chỉnh LineEdit
#         self.parent.leditPLCHost.setEnabled(command)
#         self.parent.leditPLCPort.setEnabled(command)
#         self.parent.leditPLCType.setEnabled(command)
#         #Tắt nút khả năng nhấn của btnSavePLC
#         self.parent.btnSavePLC.setEnabled(command)
#     #Set style cho nút
#     def SetStyleSheetForbtn(self, btn, background_color):
#         #Style cho nút 
#         button = getattr(self.parent, btn)
#         button.setStyleSheet(f"""
#                 QPushButton#{btn} {{
#                     border-radius: 15px;
#                     border-color: white;
#                     background-color: {background_color};  /* Màu nền mới */
#                     color: white;
#                     text-align: center;
#                     font-family: Inter, sans-serif;
#                 }}

#                 QPushButton#{btn}:hover {{
#                     background-color: #FFA500;  /* Màu nền khi hover */
#                 }}

#                 QPushButton#{btn}:pressed {{
#                     padding-left: 5px;
#                     padding-top: 5px;
#                 }}
#                 """)
#     #Import dữ liệu từ DB
#     def ImportDataFromDB(self):
#         c = self.conn.cursor()
#         #Lấy rowid từ Account
#         RowId = c.execute("SELECT rowid FROM Account WHERE UserName = ?", (self.KeyPrimary,)).fetchall()
#         #Hiển thị FullName từ Account
#         self.FullName = c.execute("SELECT FullName FROM Account WHERE rowid = ?", RowId[0]).fetchone()
#         self.parent.label_3.setText(self.FullName[0])
#         #Hiển thị Duty từ Account
#         self.Duty = c.execute("SELECT Duty FROM Account WHERE rowid = ?", RowId[0]).fetchone()
#         self.parent.label_5.setText(self.Duty[0])
#         #Hiển thị PCLHost từ Account
#         self.PLCHost = c.execute("SELECT PLCHost FROM Account WHERE rowid = ?", RowId[0]).fetchone()
#         #giải mã self.PLCHost 
#         self.key = c.execute("SELECT key FROM Account WHERE rowid = ?", RowId[0]).fetchone()
#         decrypted_data = self.decrypt_ip(self.PLCHost[0], self.key[0])
#         self.parent.leditPLCHost.setText(decrypted_data)
#         #Hiển thị PLCPort từ Account
#         self.PLCPort = c.execute("SELECT PLCPort FROM Account WHERE rowid = ?", RowId[0]).fetchone()
#         self.parent.leditPLCPort.setText(str(self.PLCPort[0])) #Chuyển sang kiểu string từ integer
#         #Hiển thị PLCType từ Account
#         self.PLCType = c.execute("SELECT PLCType FROM Account WHERE rowid = ?", RowId[0]).fetchone()
#         self.parent.leditPLCType.setText(self.PLCType[0])
#     #Cập nhật dữ liệu vào DB
#     def ModifyDataDB(self):
#         c = self.conn.cursor()
#         #Lấy rowid từ Account
#         RowId = c.execute("SELECT rowid FROM Account WHERE UserName = ?", (self.KeyPrimary,)).fetchall()
#         #Cập nhật PLCHost từ Account
#         # Mã hóa PLCHost từ self.parent.leditPLCHost.text() được nhập
#         key = Fernet.generate_key() # Tạo khóa mới
#         ip_address = self.parent.leditPLCHost.text()
#         encrypted_ip = self.encrypt_ip(ip_address, key)
#         c.execute("UPDATE Account SET PLCHost = ? WHERE rowid = ?", (encrypted_ip, RowId[0][0]))
#         #Cập nhật key từ Account
#         c.execute("UPDATE Account SET key = ? WHERE rowid = ?", (key, RowId[0][0]))
#         #Cập nhật PLCPort từ Account
#         c.execute("UPDATE Account SET PLCPort = ? WHERE rowid = ?", (self.parent.leditPLCPort.text(), RowId[0][0]))
#         #Cập nhật PLCType từ Account
#         c.execute("UPDATE Account SET PLCType = ? WHERE rowid = ?", (self.parent.leditPLCType.text(), RowId[0][0]))
#         self.conn.commit()

#      # 🔹 Hiệu ứng nhấp nháy
#     # 1.1 Hiệu ứng nhấp nháy
#     def blink_effect(self):
#         if self.blink_count >= self.blink_time:
#             self.blink_timer.stop()  # Dừng nhấp nháy
#             return

#         color = self.blink_colors[self.blink_count % 2]  # Chọn màu
#         for label in PageInitialBackend.FailedLabels:
#             self.SetStyleSheetLable(label, color)

#         self.blink_count += 1
#     # 1.2 Đặt lại trạng thái kết nối
#     def reset_connection_status(self):
#         self.blink_timer.stop()  # Đảm bảo nhấp nháy dừng
#         for label in PageInitialBackend.FailedLabels:
#             self.SetStyleSheetLable(label, "#A4A4A4")  # Đổi về màu xám

#         self.parent.btnSystemConnection.setEnabled(True)
#         self.parent.btnSystemConnection.setText("Kết nối lại")

#         PageInitialBackend.FailedLabels.clear()  # Xóa danh sách lỗi
#     # 2.1 Kiểm tra Kết nối camera
#     def CheckCameraConnection(self):
#         if PageInitialBackend.CameraConnected:
#             try: 
#                 IpAddress = PageInitialBackend.Camera.GetFeature("GevCurrentIPAddress").GetString()
#                 print("Camera connection is active.")
#                 PageInitialBackend.CameraConnected = True
#                 return True
#             except (neoapi.NeoException, Exception) as e:
#                 print(f"Error checking camera connection: {e}")
#                 #self.error_logs.append(str(e))
#                 PageInitialBackend.CameraConnected = False
#                 # Nếu không có kết nối thì thử kết nối lại
#                 print("Attempting to reconnect to Camera...")
#                 return False
#         else:
#             print("Camera connection lost.")
#             return False
#     # Thiết lập camera ban đầu
#     def init_camera(self):
#         """Khởi tạo kết nối với camera nếu chưa kết nối, nhưng vẫn cài đặt lại thông số"""
#         # Kiểm tra camera có kết nối chưa
#         if not hasattr(PageInitialBackend, "camera") or PageInitialBackend.Camera is None or not PageInitialBackend.Camera.IsConnected():
#             try:
#                 PageInitialBackend.Camera = neoapi.Cam()
#                 PageInitialBackend.Camera.Connect()
#                 print("Camera đã được kết nối!")
#                 PageInitialBackend.CameraConnected = True
#             except Exception as e:
#                 print("Lỗi khi kết nối camera:", e)
#                 PageInitialBackend.Camera = None
#                 PageInitialBackend.CameraConnected = False
#                 return  # Dừng hàm nếu kết nối thất bại

#         try:
#             # Kiểm tra & đặt chế độ lấy ảnh
#             if PageInitialBackend.Camera.f.AcquisitionMode.IsWritable():
#                 PageInitialBackend.Camera.f.AcquisitionMode.SetString("Continuous")

#             # Kiểm tra & đặt định dạng ảnh
#             pixel_format = None
#             if PageInitialBackend.Camera.f.PixelFormat.GetEnumValueList().IsReadable('BayerRG8'):
#                 pixel_format = 'BayerRG8'
#             elif PageInitialBackend.Camera.f.PixelFormat.GetEnumValueList().IsReadable('Mono8'):
#                 pixel_format = 'Mono8'

#             if pixel_format:
#                 PageInitialBackend.Camera.f.PixelFormat.SetString(pixel_format)
#                 print(f"Định dạng ảnh được đặt: {pixel_format}")
#             else:
#                 print("Không tìm thấy định dạng ảnh phù hợp!")
#                 return
#             # Kiểm tra & đặt thời gian phơi sáng
#             if PageInitialBackend.Camera.f.ExposureTime.IsWritable():
#                 PageInitialBackend.Camera.f.ExposureTime.Set(2500)
#                 print("Đặt thời gian phơi sáng: 2500")

#             # Kiểm tra & đặt tốc độ khung hình
#             if PageInitialBackend.Camera.f.AcquisitionFrameRateEnable.IsWritable():
#                 PageInitialBackend.Camera.f.AcquisitionFrameRateEnable.value = True
#             if PageInitialBackend.Camera.f.AcquisitionFrameRate.IsWritable():
#                 PageInitialBackend.Camera.f.AcquisitionFrameRate.value = 30
#                 print("Đặt tốc độ khung hình: 30 FPS")

#             # Kiểm tra & tắt Trigger Mode (nếu cần)
#             if PageInitialBackend.Camera.f.TriggerMode.IsWritable():
#                 PageInitialBackend.Camera.f.TriggerMode.SetString("Off")

#             # Bắt đầu nhận ảnh từ camera
#             if PageInitialBackend.Camera.f.AcquisitionStart.IsWritable():
#                 PageInitialBackend.Camera.f.AcquisitionStart.Execute()
#                 print("Camera đã bắt đầu truyền hình ảnh!")

#         except Exception as e:
#             print("Lỗi khi thiết lập thông số camera:", e)
#     #Hiển thị video
#     def ShowVideo(self):
#         try:
#             # Kiểm tra camera có tồn tại không
#             if not hasattr(PageInitialBackend, "Camera") or PageInitialBackend.Camera is None:
#                 print("Lỗi: Camera chưa được khởi tạo!")
#                 return
#             # Lấy ảnh từ camera
#             image = PageInitialBackend.Camera.GetImage()
#             if image is None:
#                 print("Không lấy được ảnh từ camera!")
#                 return
#             frame = image.GetNPArray()
#             if frame is None or frame.size == 0:
#                 print("Ảnh nhận được trống! Bỏ qua frame này1.")
#                 return
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             #Lưu ảnh
#             rectangles = [
#             (350, 390, 1500, 30),
#             (350, 1580, 1500, 30),
#             (2325, 420, 30, 1200),  
#                 ]
#             for idx,(x, y, w, h) in enumerate(rectangles):
#             # Cắt ảnh trong vùng hình chữ nhật
#                 roi = frame[y:y+h, x:x+w]
                
#                 # Tính tổng pixel trong vùng
#                 total_pixels = roi.sum()

#                  # Xác định màu vẽ
#                 if idx < 2:  # Hình chữ nhật 1 và 2
#                     color = (0, 255, 0) if 2400000 <= total_pixels <= 3450000 else (0, 0, 255)
#                 else:  # Hình chữ nhật 3
#                     color = (0, 255, 0) if 300000 <= total_pixels <= 420000 else (0, 0, 255)
                
#                 # Vẽ hình chữ nhật lên ảnh
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
#                 # Hiển thị tổng pixel trên ảnh
#                 cv2.putText(frame, f"{total_pixels}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
#                             1, (255, 0, 0), 2)
                
#             # Chuyển đổi từ numpy array sang QImage
#             height, width, channel = frame.shape
#             bytes_per_line = 3 * width
#             q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
#             pixmap = QPixmap.fromImage(q_image)
#             scaled_pixmap = pixmap.scaled(900, 640, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
#             # Hiển thị ảnh trên QLabel
#             self.parent.label_6.setPixmap(scaled_pixmap)
#         except Exception as e:
#             #print("Lỗi khi lấy ảnh từ camera:", e)
#             pass
#     #Thực thi nút kết nối hệ thống
#     def handleSystemConnection(self):
#         self.CameraName = None
#         if self.SystemConnection():  # Chỉ gọi SystemConnection() khi nhấn nút
#             self.init_camera()
#             # Tạo timer để gọi ShowVideo() liên tục
#             self.VideoTimer = QTimer()
#             self.VideoTimer.timeout.connect(self.ShowVideo)
#             self.VideoTimer.start(30)
#             #Cho phép chuyển trang
#             self.AllowChangePage()
#     #Dừng video
#     def StopVideo(self):
#         """Dừng video bằng cách tắt QTimer"""
#         if hasattr(self, 'VideoTimer') and self.VideoTimer.isActive():
#             self.VideoTimer.stop()
#             print("Video đã dừng!")

#     def HandleBtnSystemConnection(self):
#         #print("Nút đã được nhấn!")
#         return True
    
#     def CheckCameraConnection1(self):
#         if self.HandleBtnSystemConnection():
#             self.checking_camera_thread = ConnectionCameraChecker(self.CheckCameraConnection)
#             self.checking_camera_thread.finished.connect(self.onCameraConnectionChecked)
#             self.checking_camera_thread.start()
#             # if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#             #     self.parent.btnRestart.setEnabled(False)
#             #     self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
#             #     self.parent.btnReset.setEnabled(False)
#             #     self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")

#     def CheckPLCConnection1(self):
#         if self.HandleBtnSystemConnection():
#             self.checking_plc_thread = ConnectionPLCChecker(self.CheckPLCConnection)
#             self.checking_plc_thread.finished.connect(self.onPLCConnectionChecked)
#             self.checking_plc_thread.start()
#             # if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#             #     self.parent.btnSystemConnection.setEnabled(False)
#             #     self.parent.btnSystemConnection.setText("Đã kết nối") 
    
#     def ConnectionMonitor(self):
#         #Nếu nút btnSystemConnection được 
#         # self.AllowChangePage()
#         if self.HandleBtnSystemConnection():
#         #     self.checking_camera_thread = ConnectionCameraChecker(self.CheckCameraConnection)
#         #     self.checking_camera_thread.finished.connect(self.onCameraConnectionChecked)
#         #     self.checking_camera_thread.start()
#         #     plc_status = self.CheckPLCConnection(self.parent.leditPLCHost.text(), int(self.parent.leditPLCPort.text()))
#         #     print("plc_status:", plc_status)
#         #     self.checking_plc_thread = ConnectionPLCChecker(plc_status)
#         #     self.checking_plc_thread.finished.connect(self.onPLCConnectionChecked)
#         #     self.checking_plc_thread.start()      
#             if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
#                 self.parent.btnSystemConnection.setEnabled(False)
#                 self.parent.btnSystemConnection.setText("Đã kết nối")
#                 self.AllowChangePage()
#             else:
#                 self.parent.btnSystemConnection.setEnabled(True)
#                 self.parent.btnSystemConnection.setText("Kết nối lại")
#                 self.parent.btnConfirm.setEnabled(False)
#                 self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
#     #Thực thi khi kết thúc kiểm tra kết nối camera
#     def onCameraConnectionChecked(self, result):
#         if result:
#             self.SetStyleSheetLable("lbCameraConnected_2", "#33D909")
#             PageInitialBackend.CameraConnected = True
#         else:
#             self.checking_camera_thread.exit()
#             self.checking_camera_thread.wait()
#             self.count_error_camera += 1
#             print("Camera connection lost1. Attempting to reconnect...")
#             # self.WritePlcVariable("M4001", 1)
#             PageInitialBackend.FailedLabels.append("lbCameraConnected_2")
#             self.VideoTimer.stop()
#             self.Error_Camera_Time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
#             if self.count_error_camera == 1:
#                 self.UpdateErrorCamera(self.Error_Camera_Time)
#             self.CheckCameraConnection1timer.stop()
#             self.parent.btnSystemConnection.setEnabled(True)
#             self.parent.btnSystemConnection.setText("Kết nối lại")
#             self.parent.btnConfirm.setEnabled(False)
#             self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
            
#             PageInitialBackend.CameraConnected = False
#             if PageInitialBackend.FailedLabels:
#                 self.blink_count = 0
#                 self.blink_timer.start(500)
#                 QTimer.singleShot(3000, self.reset_connection_status) 
#     #Thực thi khi kết thúc kiểm tra kết nối PLC
#     def onPLCConnectionChecked(self, result):
#         if result:
#             self.SetStyleSheetLable("lbPLCConnected_2", "#33D909")
#             PageInitialBackend.PLCConnected = True
#             # self.WritePlcVariable("M4022", 1)
#         else:
#             self.checking_plc_thread.exit()
#             self.checking_plc_thread.wait()
#             self.count_error_plc += 1
#             print("PLC connection lost1. Attempting to reconnect...")
#             # self.VideoTimer.stop()
#             PageInitialBackend.FailedLabels.append("lbPLCConnected_2")
#             self.Error_PLC_Time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
#             if self.count_error_plc == 1:
#                 self.UpdateErrorPLC(self.Error_PLC_Time)
#             self.CheckPLCConnection1timer.stop()
#             #self.parent.btnSystemConnection.setEnabled(True)
#             self.parent.btnSystemConnection.setText("Kết nối lại")
#             self.parent.btnConfirm.setEnabled(False)
#             self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
#             PageInitialBackend.PLCConnected = False
#             if PageInitialBackend.FailedLabels:
#                 self.blink_count = 0
#                 self.blink_timer.start(500)
#                 QTimer.singleShot(3000, self.reset_connection_status)        
#     #Cho phép chuyển trang
#     def AllowChangePage(self):
#         #print(self.parent.btnSystemConnection.text())
#         if self.parent.btnSystemConnection.text() == "Đã kết nối":
#             self.parent.btnConfirm.setEnabled(True)
#             self.SetStyleSheetForbtn("btnConfirm", "#33D909")
#             #print("Allow change page")
#         else:
#             self.parent.btnConfirm.setEnabled(False)
#             self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
#             #print("Not allow change page")
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
    
#     def del_thread(self):
#         if hasattr(self, 'VideoTimer') and self.VideoTimer.isActive():
#             self.VideoTimer.stop()
#         if hasattr(self, 'CheckCameraConnection1timer') and self.CheckCameraConnection1timer.isActive():
#             self.CheckCameraConnection1timer.stop()
#         if hasattr(self, 'CheckPLCConnection1timer') and self.CheckPLCConnection1timer.isActive():
#             self.CheckPLCConnection1timer.stop()
#         if hasattr(self, 'ConnectionMonitorTimer') and self.ConnectionMonitorTimer.isActive():
#             self.ConnectionMonitorTimer.stop()
#     # Mã hóa địa chỉ IP
#     def encrypt_ip(self, ip_address: str, key: bytes) -> str:
#         fernet = Fernet(key)
#         encrypted_ip = fernet.encrypt(ip_address.encode()).decode()
#         return encrypted_ip
#     def decrypt_ip(self, encrypted_ip: str, key: bytes) -> str:
#         fernet = Fernet(key)
#         decrypted_ip = fernet.decrypt(encrypted_ip.encode()).decode()
#         return decrypted_ip   
#     def Push_working_history(self, action_name: str):
#         action_time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
#         c = self.conn.cursor()
#         #Lưu vào database
#         c.execute("INSERT INTO WorkingHistory (FullName, Duty, ActionName, ActionTime) VALUES (?, ?, ?, ?)",
#                 (self.FullName[0], self.Duty[0], action_name, action_time))
        
#         self.conn.commit()
#     def WritePlcVariable(self, address, value1):
#         if PageInitialBackend.PLCConnected:
#             try:
#                 #Ghi một giá trị bit vào PLC
#                 tag = Tag(device=address, value=value1, type=DT.BIT)
#                 PageInitialBackend.Plc.write(devices=[tag])
#                 print(f"Đã ghi giá trị {value1} vào {address}")
#             except Exception as e:
#                 print(f"Lỗi khi ghi dữ liệu vào PLC: {e}")
# #######################################################################

from MainUI1 import Ui_MainWindow
from PyQt6 import QtCore
import pandas as pd
from pymelsec import Type3E
from pymelsec.constants import DT
import neoapi
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
import sys
from CheckingCamera import ConnectionCameraChecker
from CheckingPLC import ConnectionPLCChecker
from cryptography.fernet import Fernet

#------------------------------------------------------------------------------------

class PageInitialBackend:
    CameraConnected = True
    Camera = None
    PLCConnected = True
    Plc = None
    FailedLabels = []
    CameraName = None
    ConnectionMonitorTimer = None
    def __init__(self, main: Ui_MainWindow, conn, KeyPrimary):
        #Thiết lập biến
        self.parent = main
        self.conn = conn
        self.KeyPrimary = KeyPrimary
        #Disable các nút
        self.parent.btnDashboard.setEnabled(False)
        self.parent.btnDashboard1.setEnabled(False)
        self.parent.btnParameter.setEnabled(False)
        self.parent.btnParameter1.setEnabled(False)
        self.FullName = []
        self.Duty = []
        #Kiểm tra kết nối DB
        if self.conn is None:
            raise Exception("Database connection is not available!")
        #Đọc file csv chứa thông tin input từ máy
        self.uri_machine_input_value = pd.read_csv(r"Document\no_rub_input_value.csv", index_col=0)
        self.dinput_addr = [*self.uri_machine_input_value['ID_Input']]
        self.dinput_type = [*self.uri_machine_input_value['Input_Type']]
        self.dinput_name = [name.strip() for name in [*self.uri_machine_input_value['Input_Name']]]
        self.dinput_index = [*self.uri_machine_input_value['Input_Index']]
        self.dinput_lenght = len(self.dinput_addr)
        self.dinput_old = [-1]*self.dinput_lenght
        #Liên kết dữ liệu từ DB
        self.ImportDataFromDB()
        #Ghi log
        self.Push_working_history("Đăng nhập vào hệ thống")
        # Xác nhận vị trí 
        self.parent.btnConfirm.setEnabled(False)
        self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
        # self.parent.btnConfirm.clicked.connect(lambda:[self.parent.stackedWidget.setCurrentWidget(self.parent.page_Parameter), self.ToggleMenu(), self.StopVideo()])
        self.parent.btnConfirm.clicked.connect(lambda:[self.parent.stackedWidget.setCurrentWidget(self.parent.page_Parameter), self.ToggleMenu(), self.Push_working_history("Xác nhận vị trí camera")])

        #Biến test
        self.error_logs = []
        self.plc_time = None
        self.checking_camera_thread = None
        self.checking_plc_thread = None
        self.count_error_camera = 0
        self.count_error_plc = 0
        
        # Hiệu ứng nhấp nháy
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_effect)
        self.blink_count = 0
        self.blink_time = 6  # 6 lần (3 giây, mỗi 0.5s)
        self.blink_colors = ["#DF2026", "#A4A4A4"]  # Đỏ - Xám
        # Ngắt kết nối trước khi kết nối lại
        if self.parent.btnSystemConnection.receivers(self.parent.btnSystemConnection.clicked) > 0:
            self.parent.btnSystemConnection.clicked.disconnect()
        #Kết nối hệ thống
        self.parent.btnSystemConnection.clicked.connect(lambda: [self.handleSystemConnection(), self.HandleBtnSystemConnection(), self.Push_working_history("Kết nối hệ thống")])
        
        #Thay đổi cấu hình PLC
        self.ModifyEmployee(False)
        self.SetStyleSheetForbtn("btnSavePLC", "#A4A4A4")
        self.parent.btnModifyPLC.clicked.connect(lambda: [self.ModifyEmployee(True),self.SetStyleSheetForbtn("btnSavePLC", "#DF2026"),self.parent.btnModifyPLC.setEnabled(False),self.SetStyleSheetForbtn("btnModifyPLC", "#A4A4A4"), self.Push_working_history("Thay đổi cấu hình PLC")])
        self.parent.btnSavePLC.clicked.connect(lambda:[self.ModifyDataDB(),self.ModifyEmployee(False),self.SetStyleSheetForbtn("btnSavePLC","#A4A4A4"),self.parent.btnModifyPLC.setEnabled(True),self.SetStyleSheetForbtn("btnModifyPLC", "#F68013"), self.Push_working_history("Lưu cấu hình PLC")])
        #Check System Connection, 3 giây kiểm tra 1 lần - Kiểm tra thực tế
        # PageInitialBackend.ConnectionMonitorTimer = QTimer()
        # PageInitialBackend.ConnectionMonitorTimer.timeout.connect(self.ConnectionMonitor)
        # self.CheckCameraConnection1timer = QTimer()
        # self.CheckCameraConnection1timer.timeout.connect(self.CheckCameraConnection1)
        # self.CheckPLCConnection1timer = QTimer()
        # self.CheckPLCConnection1timer.timeout.connect(self.CheckPLCConnection1)
        

    #Thiết lập bar side cho giao diện    
    def ToggleMenu(self):
        if self.parent.widgetOpen.isHidden():
            self.parent.stackedWidget.setMinimumSize(QtCore.QSize(1415, 789))
            self.parent.stackedWidget.setMaximumSize(QtCore.QSize(1415, 789))
        elif self.parent.widgetClose.isHidden():
            self.parent.stackedWidget.setMinimumSize(QtCore.QSize(1325, 789))
            self.parent.stackedWidget.setMaximumSize(QtCore.QSize(1325, 789))
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
            # self.CheckPLCConnection1timer.start(5000)
        except Exception as e:
            print(f"Error connecting to PLC: {e}")
            PageInitialBackend.PLCConnected = False
            return False
    #Kiểm tra kết nối PLC
    def CheckPLCConnection(self):
        if PageInitialBackend.PLCConnected:
            try:
                # Đọc một biến trạng thái từ PLC để kiểm tra kết nối
                read_result = PageInitialBackend.Plc.batch_read(ref_device='SM400',
                                                    read_size=1, 
                                                    data_type=DT.BIT)
                PageInitialBackend.PLCConnected = True      
                print("PLC connection is active.")
                return True    
            except Exception:
                print("PLC connection lost.")
                PageInitialBackend.PLCConnected = False  # mất kết nối
                return False
        else:
            PageInitialBackend.Plc.close()
            print("PLC connection lost1.")
            # self.PLCConnection(self.parent.leditPLCHost.text(), int(self.parent.leditPLCPort.text()), self.parent.leditPLCType.text())
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
                # self.CheckCameraConnection1timer.start(5000)
                return True
            else:
                PageInitialBackend.CameraConnected = False
                raise Exception("Camera not connected.")
        except (neoapi.NeoException, Exception) as e:
            print(f"Error checking camera connection1: {e}")
            #error_logs.append(str(e))
            PageInitialBackend.CameraConnected = False
            return False
    #Kết nối PLC và Camera
    def SystemConnection(self):
        # self.CameraConnection()
        # self.PLCConnection(self.parent.leditPLCHost.text(), int(self.parent.leditPLCPort.text()), self.parent.leditPLCType.text())
        self.Error_Camera_Time = 0
        self.Error_PLC_Time = 0
        if PageInitialBackend.PLCConnected:
            self.SetStyleSheetLable("lbPLCConnected_2", "#33D909")
        else:
            PageInitialBackend.FailedLabels.append("lbPLCConnected_2")

        if PageInitialBackend.CameraConnected:
            self.SetStyleSheetLable("lbCameraConnected_2", "#33D909")
        else:
            PageInitialBackend.FailedLabels.append("lbCameraConnected_2")

         # Nếu có lỗi, bắt đầu nhấp nháy
        if PageInitialBackend.FailedLabels:
            self.blink_count = 0
            self.blink_timer.start(500)  # Mỗi 0.5 giây
            QTimer.singleShot(3000, self.reset_connection_status)  # Sau 3 giây reset

        #if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
        if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
            # PageInitialBackend.ConnectionMonitorTimer.start(1000)
            # self.CheckCameraConnection1timer.start(5000)
            # self.CheckPLCConnection1timer.start(5000)
            print("System Connection")
            self.parent.btnSystemConnection.setEnabled(False)
            self.parent.btnSystemConnection.setText("Đã kết nối")
            # self.ShowVideo()
            self.AllowChangePage()
            return True
        else:
            self.parent.btnSystemConnection.setEnabled(False)
            self.parent.btnSystemConnection.setText("Đang kết nối")
    #Set style cho lable
    def SetStyleSheetLable(self, object, background_color):
        #Style cho nút btnEmployeeWorking
        button = getattr(self.parent, object)
        button.setStyleSheet(f"""
                QLabel#{object} {{
                    border-radius: 15px;
                    border-color: white;
                    background-color: {background_color};  /* Màu nền mới */
                    color: white;
                    text-align: center;
                    font-family: Inter, sans-serif;
                }}""")
    #Cho phép điều chỉnh cấu hình PLC
    def ModifyEmployee(self,command):
        #Cho phép điều chỉnh LineEdit
        self.parent.leditPLCHost.setEnabled(command)
        self.parent.leditPLCPort.setEnabled(command)
        self.parent.leditPLCType.setEnabled(command)
        #Tắt nút khả năng nhấn của btnSavePLC
        self.parent.btnSavePLC.setEnabled(command)
    #Set style cho nút
    def SetStyleSheetForbtn(self, btn, background_color):
        #Style cho nút 
        button = getattr(self.parent, btn)
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
    #Import dữ liệu từ DB
    def ImportDataFromDB(self):
        c = self.conn.cursor()
        #Lấy rowid từ Account
        RowId = c.execute("SELECT rowid FROM Account WHERE UserName = ?", (self.KeyPrimary,)).fetchall()
        #Hiển thị FullName từ Account
        self.FullName = c.execute("SELECT FullName FROM Account WHERE rowid = ?", RowId[0]).fetchone()
        self.parent.label_3.setText(self.FullName[0])
        #Hiển thị Duty từ Account
        self.Duty = c.execute("SELECT Duty FROM Account WHERE rowid = ?", RowId[0]).fetchone()
        self.parent.label_5.setText(self.Duty[0])
        #Hiển thị PCLHost từ Account
        self.PLCHost = c.execute("SELECT PLCHost FROM Account WHERE rowid = ?", RowId[0]).fetchone()
        #giải mã self.PLCHost 
        self.key = c.execute("SELECT key FROM Account WHERE rowid = ?", RowId[0]).fetchone()
        decrypted_data = self.decrypt_ip(self.PLCHost[0], self.key[0])
        self.parent.leditPLCHost.setText(decrypted_data)
        #Hiển thị PLCPort từ Account
        self.PLCPort = c.execute("SELECT PLCPort FROM Account WHERE rowid = ?", RowId[0]).fetchone()
        self.parent.leditPLCPort.setText(str(self.PLCPort[0])) #Chuyển sang kiểu string từ integer
        #Hiển thị PLCType từ Account
        self.PLCType = c.execute("SELECT PLCType FROM Account WHERE rowid = ?", RowId[0]).fetchone()
        self.parent.leditPLCType.setText(self.PLCType[0])
    #Cập nhật dữ liệu vào DB
    def ModifyDataDB(self):
        c = self.conn.cursor()
        #Lấy rowid từ Account
        RowId = c.execute("SELECT rowid FROM Account WHERE UserName = ?", (self.KeyPrimary,)).fetchall()
        #Cập nhật PLCHost từ Account
        #Mã hóa PLCHost từ self.parent.leditPLCHost.text() được nhập
        key = Fernet.generate_key() # Tạo khóa mới
        ip_address = self.parent.leditPLCHost.text()
        encrypted_ip = self.encrypt_ip(ip_address, key)
        c.execute("UPDATE Account SET PLCHost = ? WHERE rowid = ?", (encrypted_ip, RowId[0][0]))
        #Cập nhật key từ Account
        c.execute("UPDATE Account SET key = ? WHERE rowid = ?", (key, RowId[0][0]))
        #Cập nhật PLCPort từ Account
        c.execute("UPDATE Account SET PLCPort = ? WHERE rowid = ?", (self.parent.leditPLCPort.text(), RowId[0][0]))
        #Cập nhật PLCType từ Account
        c.execute("UPDATE Account SET PLCType = ? WHERE rowid = ?", (self.parent.leditPLCType.text(), RowId[0][0]))
        self.conn.commit()
     # 🔹 Hiệu ứng nhấp nháy
    # 1.1 Hiệu ứng nhấp nháy
    def blink_effect(self):
        if self.blink_count >= self.blink_time:
            self.blink_timer.stop()  # Dừng nhấp nháy
            return

        color = self.blink_colors[self.blink_count % 2]  # Chọn màu
        for label in PageInitialBackend.FailedLabels:
            self.SetStyleSheetLable(label, color)

        self.blink_count += 1
    # 1.2 Đặt lại trạng thái kết nối
    def reset_connection_status(self):
        self.blink_timer.stop()  # Đảm bảo nhấp nháy dừng
        for label in PageInitialBackend.FailedLabels:
            self.SetStyleSheetLable(label, "#A4A4A4")  # Đổi về màu xám

        self.parent.btnSystemConnection.setEnabled(True)
        self.parent.btnSystemConnection.setText("Kết nối lại")

        PageInitialBackend.FailedLabels.clear()  # Xóa danh sách lỗi
    # 2.1 Kiểm tra Kết nối camera
    def CheckCameraConnection(self):
        if PageInitialBackend.CameraConnected:
            try: 
                IpAddress = PageInitialBackend.Camera.GetFeature("GevCurrentIPAddress").GetString()
                #print("Camera connection is active.")
                PageInitialBackend.CameraConnected = True
                return True
            except (neoapi.NeoException, Exception) as e:
                print(f"Error checking camera connection: {e}")
                #self.error_logs.append(str(e))
                PageInitialBackend.CameraConnected = False
                # Nếu không có kết nối thì thử kết nối lại
                print("Attempting to reconnect to Camera...")
                return False
        else:
            print("Camera connection lost.")
            return False
    # Thiết lập camera ban đầu
    def init_camera(self):
        """Khởi tạo kết nối với camera nếu chưa kết nối, nhưng vẫn cài đặt lại thông số"""
        
        # Kiểm tra camera có kết nối chưa
        if not hasattr(PageInitialBackend, "camera") or PageInitialBackend.Camera is None or not PageInitialBackend.Camera.IsConnected():
            try:
                PageInitialBackend.Camera = neoapi.Cam()
                PageInitialBackend.Camera.Connect()
                print("Camera đã được kết nối!")
                PageInitialBackend.CameraConnected = True
            except Exception as e:
                print("Lỗi khi kết nối camera:", e)
                PageInitialBackend.Camera = None
                PageInitialBackend.CameraConnected = False
                return  # Dừng hàm nếu kết nối thất bại

        try:
            # Kiểm tra & đặt chế độ lấy ảnh
            if PageInitialBackend.Camera.f.AcquisitionMode.IsWritable():
                PageInitialBackend.Camera.f.AcquisitionMode.SetString("Continuous")

            # Kiểm tra & đặt định dạng ảnh
            pixel_format = None
            if PageInitialBackend.Camera.f.PixelFormat.GetEnumValueList().IsReadable('BayerRG8'):
                pixel_format = 'BayerRG8'
            elif PageInitialBackend.Camera.f.PixelFormat.GetEnumValueList().IsReadable('Mono8'):
                pixel_format = 'Mono8'

            if pixel_format:
                PageInitialBackend.Camera.f.PixelFormat.SetString(pixel_format)
                print(f"Định dạng ảnh được đặt: {pixel_format}")
            else:
                print("Không tìm thấy định dạng ảnh phù hợp!")
                return
            # Kiểm tra & đặt thời gian phơi sáng
            if PageInitialBackend.Camera.f.ExposureTime.IsWritable():
                PageInitialBackend.Camera.f.ExposureTime.Set(2500)
                print("Đặt thời gian phơi sáng: 2500")

            # Kiểm tra & đặt tốc độ khung hình
            if PageInitialBackend.Camera.f.AcquisitionFrameRateEnable.IsWritable():
                PageInitialBackend.Camera.f.AcquisitionFrameRateEnable.value = True
            if PageInitialBackend.Camera.f.AcquisitionFrameRate.IsWritable():
                PageInitialBackend.Camera.f.AcquisitionFrameRate.value = 30
                print("Đặt tốc độ khung hình: 30 FPS")

            # Kiểm tra & tắt Trigger Mode (nếu cần)
            if PageInitialBackend.Camera.f.TriggerMode.IsWritable():
                PageInitialBackend.Camera.f.TriggerMode.SetString("Off")

            # Bắt đầu nhận ảnh từ camera
            if PageInitialBackend.Camera.f.AcquisitionStart.IsWritable():
                PageInitialBackend.Camera.f.AcquisitionStart.Execute()
                print("Camera đã bắt đầu truyền hình ảnh!")

        except Exception as e:
            print("Lỗi khi thiết lập thông số camera:", e)
    #Hiển thị video
    def ShowVideo(self):
        try:
            # Kiểm tra camera có tồn tại không
            if not hasattr(PageInitialBackend, "Camera") or PageInitialBackend.Camera is None:
                print("Lỗi: Camera chưa được khởi tạo!")
                return
            # Lấy ảnh từ camera
            image = PageInitialBackend.Camera.GetImage()
            if image is None:
                print("Không lấy được ảnh từ camera!")
                return
            frame = image.GetNPArray()
            if frame is None or frame.size == 0:
                print("Ảnh nhận được trống! Bỏ qua frame này1.")
                return
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #Lưu ảnh
            rectangles = [
            (350, 390, 1500, 30),
            (350, 1580, 1500, 30),
            (2325, 420, 30, 1200),  
                ]
            for idx,(x, y, w, h) in enumerate(rectangles):
            # Cắt ảnh trong vùng hình chữ nhật
                roi = frame[y:y+h, x:x+w]
                
                # Tính tổng pixel trong vùng
                total_pixels = roi.sum()

                 # Xác định màu vẽ
                if idx < 2:  # Hình chữ nhật 1 và 2
                    color = (0, 255, 0) if 2400000 <= total_pixels <= 3450000 else (0, 0, 255)
                else:  # Hình chữ nhật 3
                    color = (0, 255, 0) if 300000 <= total_pixels <= 420000 else (0, 0, 255)
                
                # Vẽ hình chữ nhật lên ảnh
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Hiển thị tổng pixel trên ảnh
                cv2.putText(frame, f"{total_pixels}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (255, 0, 0), 2)
                
            # Chuyển đổi từ numpy array sang QImage
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(900, 640, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            # Hiển thị ảnh trên QLabel
            self.parent.label_6.setPixmap(scaled_pixmap)
        except Exception as e:
            #print("Lỗi khi lấy ảnh từ camera:", e)
            pass
    #Thực thi nút kết nối hệ thống
    def handleSystemConnection(self):
        self.CameraName = None
        if self.SystemConnection():  # Chỉ gọi SystemConnection() khi nhấn nút
            # self.init_camera()
            # Tạo timer để gọi ShowVideo() liên tục
            # self.VideoTimer = QTimer()
            # self.VideoTimer.timeout.connect(self.ShowVideo)
            # self.VideoTimer.start(30)
            #Cho phép chuyển trang
            self.AllowChangePage()
    #Dừng video
    def StopVideo(self):
        """Dừng video bằng cách tắt QTimer"""
        if hasattr(self, 'VideoTimer') and self.VideoTimer.isActive():
            self.VideoTimer.stop()
            print("Video đã dừng!")

    def HandleBtnSystemConnection(self):
        #print("Nút đã được nhấn!")
        return True
    
    def CheckCameraConnection1(self):
        if self.HandleBtnSystemConnection():
            self.checking_camera_thread = ConnectionCameraChecker(self.CheckCameraConnection)
            self.checking_camera_thread.finished.connect(self.onCameraConnectionChecked)
            self.checking_camera_thread.start()
            # if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
            #     self.parent.btnRestart.setEnabled(False)
            #     self.SetStyleSheetForbtn("btnRestart", "#A4A4A4", "15px")
            #     self.parent.btnReset.setEnabled(False)
            #     self.SetStyleSheetForbtn("btnReset", "#A4A4A4", "15px")

    def CheckPLCConnection1(self):
        if self.HandleBtnSystemConnection():
            self.checking_plc_thread = ConnectionPLCChecker(self.CheckPLCConnection)
            self.checking_plc_thread.finished.connect(self.onPLCConnectionChecked)
            self.checking_plc_thread.start()
            # if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
            #     self.parent.btnSystemConnection.setEnabled(False)
            #     self.parent.btnSystemConnection.setText("Đã kết nối") 
    
    def ConnectionMonitor(self):
        #Nếu nút btnSystemConnection được 
        # self.AllowChangePage()
        if self.HandleBtnSystemConnection():
        #     self.checking_camera_thread = ConnectionCameraChecker(self.CheckCameraConnection)
        #     self.checking_camera_thread.finished.connect(self.onCameraConnectionChecked)
        #     self.checking_camera_thread.start()
        #     plc_status = self.CheckPLCConnection(self.parent.leditPLCHost.text(), int(self.parent.leditPLCPort.text()))
        #     print("plc_status:", plc_status)
        #     self.checking_plc_thread = ConnectionPLCChecker(plc_status)
        #     self.checking_plc_thread.finished.connect(self.onPLCConnectionChecked)
        #     self.checking_plc_thread.start()      
            if PageInitialBackend.PLCConnected and PageInitialBackend.CameraConnected:
                self.parent.btnSystemConnection.setEnabled(False)
                self.parent.btnSystemConnection.setText("Đã kết nối")
                self.AllowChangePage()
            else:
                self.parent.btnSystemConnection.setEnabled(True)
                self.parent.btnSystemConnection.setText("Kết nối lại")
                self.parent.btnConfirm.setEnabled(False)
                self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
    #Thực thi khi kết thúc kiểm tra kết nối camera
    def onCameraConnectionChecked(self, result):
        if result:
            self.SetStyleSheetLable("lbCameraConnected_2", "#33D909")
            PageInitialBackend.CameraConnected = True
        else:
            self.checking_camera_thread.exit()
            self.checking_camera_thread.wait()
            self.count_error_camera += 1
            print("Camera connection lost1. Attempting to reconnect...")
            PageInitialBackend.FailedLabels.append("lbCameraConnected_2")
            self.VideoTimer.stop()
            self.Error_Camera_Time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            if self.count_error_camera == 1:
                self.UpdateErrorCamera(self.Error_Camera_Time)
            self.CheckCameraConnection1timer.stop()
            self.parent.btnSystemConnection.setEnabled(True)
            self.parent.btnSystemConnection.setText("Kết nối lại")
            self.parent.btnConfirm.setEnabled(False)
            self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
            
            PageInitialBackend.CameraConnected = False
            if PageInitialBackend.FailedLabels:
                self.blink_count = 0
                self.blink_timer.start(500)
                QTimer.singleShot(3000, self.reset_connection_status) 
    #Thực thi khi kết thúc kiểm tra kết nối PLC
    def onPLCConnectionChecked(self, result):
        if result:
            self.SetStyleSheetLable("lbPLCConnected_2", "#33D909")
            PageInitialBackend.PLCConnected = True
        else:
            self.checking_plc_thread.exit()
            self.checking_plc_thread.wait()
            self.count_error_plc += 1
            print("PLC connection lost1. Attempting to reconnect...")
            # self.VideoTimer.stop()
            PageInitialBackend.FailedLabels.append("lbPLCConnected_2")
            self.Error_PLC_Time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            if self.count_error_plc == 1:
                self.UpdateErrorPLC(self.Error_PLC_Time)
            self.CheckPLCConnection1timer.stop()
            #self.parent.btnSystemConnection.setEnabled(True)
            self.parent.btnSystemConnection.setText("Kết nối lại")
            self.parent.btnConfirm.setEnabled(False)
            self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
            PageInitialBackend.PLCConnected = False
            PageInitialBackend.Plc.close()
            if PageInitialBackend.FailedLabels:
                self.blink_count = 0
                self.blink_timer.start(500)
                QTimer.singleShot(3000, self.reset_connection_status)        
    #Cho phép chuyển trang
    def AllowChangePage(self):
        #print(self.parent.btnSystemConnection.text())
        if self.parent.btnSystemConnection.text() == "Đã kết nối":
            self.parent.btnConfirm.setEnabled(True)
            self.SetStyleSheetForbtn("btnConfirm", "#33D909")
            #print("Allow change page")
        else:
            self.parent.btnConfirm.setEnabled(False)
            self.SetStyleSheetForbtn("btnConfirm", "#A4A4A4")
            #print("Not allow change page")
    #Lưu vào database lỗi camera
    def UpdateErrorCamera(self, timestamp):
        #Lưu vào database
        c = self.conn.cursor()
        c.execute("INSERT INTO ErrorHistory (ErrorName, ProductName, Timestamp) VALUES (?, ?, ?)",
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
    
    def del_thread(self):
        if hasattr(self, 'VideoTimer') and self.VideoTimer.isActive():
            self.VideoTimer.stop()
        if hasattr(self, 'CheckCameraConnection1timer') and self.CheckCameraConnection1timer.isActive():
            self.CheckCameraConnection1timer.stop()
        if hasattr(self, 'CheckPLCConnection1timer') and self.CheckPLCConnection1timer.isActive():
            self.CheckPLCConnection1timer.stop()
        if hasattr(self, 'ConnectionMonitorTimer') and self.ConnectionMonitorTimer.isActive():
            self.ConnectionMonitorTimer.stop()
    #Mã hóa địa chỉ IP
    def encrypt_ip(self, ip_address: str, key: bytes) -> str:
        fernet = Fernet(key)
        encrypted_ip = fernet.encrypt(ip_address.encode()).decode()
        return encrypted_ip
    #Giải mã địa chỉ IP
    def decrypt_ip(self, encrypted_ip: str, key: bytes) -> str:
        fernet = Fernet(key)
        decrypted_ip = fernet.decrypt(encrypted_ip.encode()).decode()
        return decrypted_ip
    
    def Push_working_history(self, action_name: str):
        action_time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        c = self.conn.cursor()
        #Lưu vào database
        c.execute("INSERT INTO WorkingHistory (FullName, Duty, ActionName, ActionTime) VALUES (?, ?, ?, ?)",
                (self.FullName[0], self.Duty[0], action_name, action_time))
        
        self.conn.commit()