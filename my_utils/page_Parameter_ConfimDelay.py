# from MainUI1 import Ui_MainWindow
# from PyQt6 import QtCore
# from page_Parameter import PageParameterBackend
# from page_Initial import PageInitialBackend
# from pymelsec import Type3E
# from pymelsec.constants import DT
# import time
# from PyQt6.QtCore import QTimer, Qt
# import os
# import cv2
# from PyQt6.QtGui import QImage, QPixmap

# class PageParameterConfirmBackend():
#     def __init__(self, main: Ui_MainWindow, conn, initial: PageInitialBackend, para: PageParameterBackend):
#         #Khai báo biến
#         self.parent = main
#         self.conn = conn
#         self.para = para
#         self.initial = initial
#         #Biến trigger
#         self.trigger = PageInitialBackend.Camera.f.TriggerSoftware  # Initialize trigger to None
#         self.para.set_confirm_page(self)
#         self.processing = False  # Trạng thái xử lý hình ảnh
#         self.last_trigger_state = 0
#         self.TriggerTimerConfirm = QTimer()
#         self.TriggerTimerConfirm.timeout.connect(self.TriggerImage)
#         self.triggered = None
#         self.image_directory = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceImages1"
#         self.confirm_page = None
#         self.Time_Start = None
#         self.Delay = []
#         #Xác nhận hoàn tất để chuyển hướng đến trang Dashboard
#         self.parent.btnParameterConfirmation1.clicked.connect(lambda: [self.open_confirm_page(), self.ToggleMenu(),self.para.SetupCameraForTrigger(), self.TriggerTimerConfirm.stop(), self.initial.del_thread(), self.Push_working_history("Xác nhận hoàn tất kiểm tra vị trí chụp sản phẩm")])
#         # self.parent.btnParameterConfirmation1.clicked.connect(lambda: [self.open_confirm_page(), self.ToggleMenu()])

#         #Không cho phép điều chỉnh thông số đèn và delay khi chưa xác nhận
#         self.LeditModify(False)
#         self.parent.leditTriggerDelay.setEnabled(False)
#         #Set style cho nút ban đầu
#         self.parent.btnSaveLight.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveLight", "#A4A4A4")
#         self.parent.btnParameterDefaultLight.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultLight", "#A4A4A4")
#         self.parent.btnTry.setEnabled(False)
#         self.SetStyleSheetForbtn("btnTry", "#A4A4A4")
#         self.parent.btnSaveCounter1.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveCounter1", "#A4A4A4")
#         self.parent.btnParameterConfirmation1.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterConfirmation1", "#A4A4A4")
#         #Hiển thị tên sản phẩm từ lbProductName1
#         #Kết nối chọn sản phẩm
#         self.updateProductName(self.parent.lbProductName1.text())
#         self.parent.label_56.setText(self.parent.lbProductName1.text())
#         #Cho phép điều chỉnh thông số đèn
#         self.parent.btnModifyLight.clicked.connect(lambda: [self.LeditModify(True), self.parent.btnModifyLight.setEnabled(False), self.SetStyleSheetForbtn("btnModifyLight", "#A4A4A4") ,self.parent.btnSaveLight.setEnabled(True), self.SetStyleSheetForbtn("btnSaveLight", "#DF2026"), self.parent.btnParameterDefaultLight.setEnabled(True), self.SetStyleSheetForbtn("btnParameterDefaultLight", "#F68013"), self.Push_working_history("Điều chỉnh thông số đèn")])
#         #Lưu thông số đèn
#         self.parent.btnSaveLight.clicked.connect(self.SaveLightConfig)
#         #Trả về thông số mặc định của đèn
#         self.parent.btnParameterDefaultLight.clicked.connect(self.DefaultLightConfig)
#         #Đếm số lần test vị trí
#         self.parent.lbTestCounter.setText("0")
#         self.ImageCounter = 0
#         self.TriggerCounterImage = QTimer()
#         self.TriggerCounterImage.timeout.connect(self.CountImage)
#         self.TriggerCounterImage.start(500)
#         #Nhấn nút thử lại
#         self.parent.btnTry.clicked.connect(lambda: [self.parent.lbImageConfirm.clear(), self.parent.label_66.setText("Hãy đưa sản phẩm vào kiểm tra"), self.parent.btnTry.setEnabled(False), self.SetStyleSheetForbtn("btnTry", "#A4A4A4"), self.StartTrigger(), self.Push_working_history("Nhấn nút thử lại vị trí chụp sản phẩm")]) 
#         # self.parent.btnTry.clicked.connect(lambda: [self.parent.lbImageConfirm.clear(), self.parent.label_66.setText("Hãy đưa sản phẩm vào kiểm tra"), self.parent.btnTry.setEnabled(False), self.SetStyleSheetForbtn("btnTry", "#A4A4A4")])
#         #btnParameterConfirmation1
#         self.parent.btnModifyCounter1.clicked.connect(lambda:[self.parent.leditTriggerDelay.setEnabled(True), self.parent.btnModifyCounter1.setEnabled(False), self.SetStyleSheetForbtn("btnModifyCounter1", "#A4A4A4"), self.parent.btnSaveCounter1.setEnabled(True), self.SetStyleSheetForbtn("btnSaveCounter1", "#DF2026"), self.Push_working_history("Điều chỉnh thông số delay")])
#         self.parent.btnSaveCounter1.clicked.connect(self.SaveCounterConfig)
#         #Cho phép qua trang Dashboard
#         self.AcceptingConfirmation()
#         self.Time_Start = QtCore.QDateTime.currentDateTime()
#         self.UpdateHistoryTime()

#     #Thiết lập bar side cho giao diện    
#     def ToggleMenu(self):
#         if self.parent.widgetOpen.isHidden():
#             self.parent.stackedWidget.setMinimumSize(QtCore.QSize(1415, 789))
#             self.parent.stackedWidget.setMaximumSize(QtCore.QSize(1415, 789))
#         elif self.parent.widgetClose.isHidden():
#             self.parent.stackedWidget.setMinimumSize(QtCore.QSize(1325, 789))
#             self.parent.stackedWidget.setMaximumSize(QtCore.QSize(1325, 789)) 
#     #Set style cho nút
#     def SetStyleSheetForbtn(self, btn, background_color):
#         #Style cho nút 
#         button = getattr(self.parent, btn)
#         button.setStyleSheet(f"""
#                 QPushButton#{btn} {{
#                     border-radius: 20px;
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
#     #Cho phép điều chỉnh thông số đèn
#     def LeditModify(self,command):
#         self.parent.leditLight1.setEnabled(command)
#         self.parent.leditLight2.setEnabled(command)
#         self.parent.leditLight3.setEnabled(command)
#         self.parent.leditLight4.setEnabled(command)
#     #Lưu thông số đèn
#     def SaveLightConfig(self):
#         self.Push_working_history("Lưu thông số đèn")

#         #Lấy text hiện tại của QLineEdit
#         light1 = self.parent.leditLight1.text()
#         light2 = self.parent.leditLight2.text()
#         light3 = self.parent.leditLight3.text()
#         light4 = self.parent.leditLight4.text()
#         #Update vào database
#         c = self.conn.cursor()
#         c.execute("UPDATE Product SET LIGHT1 = ?, LIGHT2 = ?, LIGHT3 = ?, LIGHT4 = ? WHERE rowid = ?", (light1, light2, light3, light4, self.RowId[0][0]))
#         self.conn.commit()
#         #Cho chép bấm nút Modify
#         self.parent.btnModifyLight.setEnabled(True)
#         self.SetStyleSheetForbtn("btnModifyLight", "#33D909")
#         #Tắt nút khả năng nhấn của btnSaveLight
#         self.parent.btnSaveLight.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveLight", "#A4A4A4")
#         #Tắt nút khả năng nhấn của btnParameterDefaultLight
#         self.parent.btnParameterDefaultLight.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultLight", "#A4A4A4")
#     #Lấy thông số mặc định của đèn
#     def DefaultLightConfig(self):
#         self.Push_working_history("Trả về thông số mặc định của đèn")
#         c = self.conn.cursor()
#         #Lấy dữ liệu từ Light1Default Database
#         Light1Default = c.execute("SELECT LIGHT1 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditLight1.setText(str(Light1Default[0]))
#         #Lấy dữ liệu từ Light2Default Database
#         Light2Default = c.execute("SELECT LIGHT2 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditLight2.setText(str(Light2Default[0]))
#         #Lấy dữ liệu từ Light3Default Database
#         Light3Default = c.execute("SELECT LIGHT3 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditLight3.setText(str(Light3Default[0]))
#         #Lấy dữ liệu từ Light4Default Database
#         Light4Default = c.execute("SELECT LIGHT4 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditLight4.setText(str(Light4Default[0]))
#         #Cho chép bấm nút Modify
#         self.parent.btnModifyLight.setEnabled(True)
#         self.SetStyleSheetForbtn("btnModifyLight", "#33D909")
#         #Tắt nút khả năng nhấn của btnSaveLight
#         self.parent.btnSaveLight.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveLight", "#A4A4A4")
#         #Tắt nút khả năng nhấn của btnParameterDefaultLight
#         self.parent.btnParameterDefaultLight.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultLight", "#A4A4A4")
#     #Cập nhật tên sản phẩm
#     def updateProductName(self, text):        
#         self.parent.label_56.setText(text)  # Cập nhật label 
#         #Lấy thông số từ database
#         c = self.conn.cursor()
#         self.RowId = c.execute("SELECT rowid FROM Product WHERE ProductName = ?", (text,)).fetchall()
#         #Hiện thị thông số  đèn 1
#         self.Light1 = c.execute("SELECT LIGHT1 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditLight1.setText(str(self.Light1[0]))
#         #Hiện thị thông số  đèn 2
#         self.Light2 = c.execute("SELECT LIGHT2 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditLight2.setText(str(self.Light2[0]))
#         #Hiện thị thông số  đèn 3
#         self.Light3 = c.execute("SELECT LIGHT3 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditLight3.setText(str(self.Light3[0]))
#         #Hiện thị thông số  đèn 4
#         self.Light4 = c.execute("SELECT LIGHT4 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditLight4.setText(str(self.Light4[0]))
#         #Hiển thị thông số delay
#         self.Delay = c.execute("SELECT TriggerDelay FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditTriggerDelay.setText(str(self.Delay[0]))
#     # Lấy biến PLC để kích hoạt camera trigger
#     def GetPlcVariableForTrigger(self):
#         if PageInitialBackend.PLCConnected == True and PageInitialBackend.CameraConnected == True:
#             for i in range(self.initial.dinput_lenght):
#                 try:
#                     # Đọc biến từ PLC
#                     read_result = PageInitialBackend.Plc.batch_read(ref_device='X0', read_size=30, data_type=DT.BIT)
#                     RealValue1 = int(read_result[29].value)
#                     if self.initial.dinput_old[20] != RealValue1:
#                         # self.TriggerTimerConfirm.stop()
#                         self.initial.dinput_old[20] = RealValue1
#                         print("S3/in/19", RealValue1)
                            
#                     trigger_value = RealValue1
#                     # Break the loop or return from the function to stop the trigger
#                     if trigger_value == 1  and self.last_trigger_state == 0:  
#                         self.triggered = True  # Đặt cờ sự kiện kích hoạt
#                         self.processing = True
#                     elif trigger_value == 0:
#                         self.processing = False  # Reset lại trạng thái xử lý khi trigger_value là 0
#                     self.last_trigger_state = trigger_value  # Cập nhật trạng thái trước của trigger_value
#                     return
#                 except Exception as e:
#                     print("Failed to get PLC variable:", e)
#                     self.triggered = False  # Đặt lại cờ sự kiện kích hoạt nếu có lỗi
#     #Xử lí hình ảnh thông qua cảm biến trigger
#     def TriggerImage(self):
#         #Lấy thông số delay từ database
#         if PageInitialBackend.PLCConnected == True and PageInitialBackend.CameraConnected == True:
#             self.GetPlcVariableForTrigger()
#             #print("Waiting for next trigger")
#             # print("Trigger state:", self.triggered)
#             if self.triggered:
#                 self.processing = True
#                 print("Trigger activated, processing images...")
#                 try:
#                     #start = time.time()
#                     # print("Delay:", self.Delay[0])
#                     time.sleep(self.Delay[0])
#                     if self.trigger:
#                         self.trigger.Execute()
#                     else:
#                         print("Trigger is not initialized.")
#                     self.img_camera = self.initial.Camera.GetImage()
#                     # file_path = self.GetNextFilename()
#                     # self.img_camera.Save(file_path)
#                     if self.img_camera is None:
#                         print("Không thể lấy ảnh từ camera!")
#                     else:
#                         print("Ảnh đã được lấy thành công!")
#                     #Hiển thị hình ảnh
#                     frame = self.img_camera.GetNPArray()
#                     if frame is None or frame.size == 0:
#                         print("Ảnh nhận được trống! Bỏ qua frame này.")
#                     else:
#                         print("Ảnh nhận được không trống! Hiển thị ảnh...")
#                     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                     height, width, channel = frame.shape
#                     x1 = int(width * 0.18)
#                     x2 = int(width * 0.84)
#                     y_start = int(height * 0.1)
#                     y_end = int(height * 0.9)
#                     line_color = (0, 255, 0)  # Màu xanh lá (R, G, B)
#                     line_thickness = 2  
#                     cv2.line(frame, (x1, y_start), (x1, y_end), line_color, line_thickness)
#                     cv2.line(frame, (x2, y_start), (x2, y_end), line_color, line_thickness)
#                     bytes_per_line = 3 * width
#                     q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
#                     pixmap = QPixmap.fromImage(q_image)
#                     scaled_pixmap = pixmap.scaled(900, 640, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
#                     self.parent.lbImageConfirm.setPixmap(scaled_pixmap)
#                     #self.CountImage()
#                     self.triggered = False  # Đặt lại trigger để chờ lần kích hoạt tiếp theo
#                     self.processing = False  
#                 except Exception as e:
#                     print(f"Error capturing or saving image: {e}")
#                     self.triggered = False
#                 finally:
#                     # Reset trigger sau khi hoàn thành xử lý
#                     self.triggered = False
#                     self.processing = False
#     #Khi nhấn nút btnTry và ImageCounter > 0
#     def StartTrigger(self):
#         if self.ImageCounter > 0:
#             self.TriggerTimerConfirm.start(10)  # Bắt đầu timer mỗi 500ms
#             self.TriggerCounterImage.start(500)
#             print("Trigger đang chạy...")
#         else:
#             print("Không thể chạy trigger, Test Counter = 0")
#     #Đếm số lần hiển thị hình ảnh
#     def CountImage(self):
#         #Kiểm tra lbImageConfirm có đang chứa hình ảnh không
#         pixmap = self.parent.lbImageConfirm.pixmap()
#         if pixmap and not pixmap.isNull():
#             self.ImageCounter += 1
#             self.parent.lbTestCounter.setText(str(self.ImageCounter))
#             self.parent.label_66.setText("Đã hiển thị hình ảnh")
#             self.parent.btnTry.setEnabled(True)
#             self.SetStyleSheetForbtn("btnTry", "#F68013")
#             self.parent.btnParameterConfirmation1.setEnabled(True)
#             self.SetStyleSheetForbtn("btnParameterConfirmation1", "#3D7AEF")
#             self.TriggerTimerConfirm.stop()
#             self.TriggerCounterImage.stop()
#         else:
#             self.parent.label_66.setText("Hãy đưa sản phẩm vào kiểm tra")
#             self.parent.btnTry.setEnabled(False)
#             self.SetStyleSheetForbtn("btnTry", "#A4A4A4")
#             self.TriggerTimerConfirm.start(10)       
#     #Xác nhận hoàn tất để chuyển hướng đến trang Dashboard
#     def AcceptingConfirmation(self):
#         if self.ImageCounter != 0:
#             self.parent.btnParameterConfirmation1.setEnabled(True)
#             self.SetStyleSheetForbtn("btnParameterConfirmation1", "#3D7AEF")
#     #Lưu thông số delay
#     def SaveCounterConfig(self):
#         self.Push_working_history("Lưu thông số delay")
#         # #Lấy text hiện tại của QLineEdit
#         # TriggerDelay = float(self.parent.leditTriggerDelay.text())
#         # Lấy text hiện tại của QLineEdit
#         self.TriggerDelay = float(self.parent.leditTriggerDelay.text())
#         #Update vào database
#         c = self.conn.cursor()
#         c.execute("UPDATE Product SET TriggerDelay = ? WHERE rowid = ?", (self.TriggerDelay, self.RowId[0][0]))
#         self.conn.commit()
#         #Cho chép bấm nút Modify
#         self.parent.btnModifyCounter1.setEnabled(True)
#         self.SetStyleSheetForbtn("btnModifyCounter1", "#33D909")
#         #Tắt nút khả năng nhấn của btnSaveLight
#         self.parent.btnSaveCounter1.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveCounter1", "#A4A4A4")
#         self.Delay = c.execute("SELECT TriggerDelay FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditTriggerDelay.setText(str(self.Delay[0]))
  
#     def GetNextFilename(self):
#         # Tìm số thứ tự tệp cuối cùng trong thư mục
#         existing_files = sorted(
#             [f for f in os.listdir(self.image_directory) if f.startswith("IMG_") and f.endswith(".bmp")]
#         )
        
#         if existing_files:
#             # Lấy số thứ tự của tệp cuối cùng và tăng lên 1
#             last_file = existing_files[-1]
#             last_number = int(last_file[4:8])  # Lấy số từ "IMG_0001.bmp"
#             next_number = (last_number + 1) % 10000  # Giới hạn từ 0000 đến 9999
#         else:
#             next_number = 1

#         return os.path.join(self.image_directory, f"IMG_{next_number:04d}.bmp")   
#     #Reset trang
#     def InitialPage(self):
#         self.trigger = PageInitialBackend.Camera.f.TriggerSoftware  # Initialize trigger to None
#         self.processing = False  # Trạng thái xử lý hình ảnh
#         self.last_trigger_state = 0
#         self.TriggerTimerConfirm = QTimer()
#         self.TriggerTimerConfirm.timeout.connect(self.TriggerImage)
#         self.parent.btnParameterConfirmation1.clicked.connect(lambda: [self.open_confirm_page(), self.ToggleMenu(), self.Push_working_history("Xác nhận hoàn tất kiểm tra vị trí chụp sản phẩm")])
#         self.triggered = None
#         self.image_directory = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceImages1"
#         self.Time_Start = None
#         self.Delay = []
#         self.LeditModify(False)
#         self.parent.leditTriggerDelay.setEnabled(False)
#         #Set style cho nút ban đầu
#         self.parent.btnSaveLight.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveLight", "#A4A4A4")
#         self.parent.btnParameterDefaultLight.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultLight", "#A4A4A4")
#         self.parent.btnTry.setEnabled(False)
#         self.SetStyleSheetForbtn("btnTry", "#A4A4A4")
#         self.parent.btnSaveCounter1.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveCounter1", "#A4A4A4")
#         self.parent.btnParameterConfirmation1.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterConfirmation1", "#A4A4A4")
#         self.parent.lbImageConfirm.clear()
#         self.updateProductName(self.parent.lbProductName1.text())
#         self.parent.label_56.setText(self.parent.lbProductName1.text())
#         #Đếm số lần test vị trí
#         self.parent.lbTestCounter.setText("0")
#         self.ImageCounter = 0
#         self.TriggerCounterImage = QTimer()
#         self.TriggerCounterImage.timeout.connect(self.CountImage)
#         self.TriggerCounterImage.start(500)
#         #Cho phép qua trang Dashboard
#         self.AcceptingConfirmation()
#         self.Time_Start = QtCore.QDateTime.currentDateTime()
#         self.UpdateHistoryTime()

#     def set_confirm_page(self, confirm_page):
#         self.confirm_page = confirm_page

#     def open_confirm_page(self):
#         print("self.confirm_page1", self.confirm_page)
#         if self.confirm_page:
#             print("open_confirm_page1")
#             self.confirm_page.initializePage()  # Gọi lại như lần đầu
#         self.parent.stackedWidget.setCurrentWidget(self.parent.page_Dashboard)

#     def UpdateHistoryTime(self):
#         #Lưu vào database
#         c = self.conn.cursor()
#         c.execute("INSERT INTO ProductHistory (ProductName, StartTime) VALUES (?, ?)", (self.parent.lbProductName1.text(), self.Time_Start.toString("yyyy-MM-dd hh:mm:ss")))
#         self.conn.commit()
#     def Push_working_history(self, action_name: str):
#         action_time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
#         c = self.conn.cursor()
#         #Lưu vào database
#         c.execute("INSERT INTO WorkingHistory (FullName, Duty, ActionName, ActionTime) VALUES (?, ?, ?, ?)",
#                 (self.initial.FullName[0], self.initial.Duty[0], action_name, action_time))
        
#         self.conn.commit()
# ########################################################################

from MainUI1 import Ui_MainWindow
from PyQt6 import QtCore
from page_Parameter import PageParameterBackend
from page_Initial import PageInitialBackend
from pymelsec.constants import DT
import time
from PyQt6.QtCore import Qt
import os
import cv2
from PyQt6.QtGui import QImage, QPixmap

class PageParameterConfirmBackend():
    def __init__(self, main: Ui_MainWindow, conn, initial: PageInitialBackend, para: PageParameterBackend):
        #Khai báo biến
        self.parent = main
        self.conn = conn
        self.para = para
        self.initial = initial
        #Biến trigger
        # self.trigger = PageInitialBackend.Camera.f.TriggerSoftware  # Initialize trigger to None
        self.para.set_confirm_page(self)
        self.processing = False  # Trạng thái xử lý hình ảnh
        self.last_trigger_state = 0
        # self.TriggerTimerConfirm = QTimer()
        # self.TriggerTimerConfirm.timeout.connect(self.TriggerImage)
        self.triggered = None
        self.image_directory = r"SourceImages1"
        self.confirm_page = None
        self.Time_Start = None
        self.Delay = []
        #Xác nhận hoàn tất để chuyển hướng đến trang Dashboard
        # self.parent.btnParameterConfirmation1.clicked.connect(lambda: [self.open_confirm_page(), self.ToggleMenu(),self.para.SetupCameraForTrigger(), self.TriggerTimerConfirm.stop(), self.initial.del_thread()])
        self.parent.btnParameterConfirmation1.clicked.connect(lambda: [self.open_confirm_page(), self.ToggleMenu(), self.Push_working_history("Xác nhận hoàn tất kiểm tra vị trí chụp sản phẩm")])

        #Không cho phép điều chỉnh thông số đèn và delay khi chưa xác nhận
        self.LeditModify(False)
        self.parent.leditTriggerDelay.setEnabled(False)
        #Set style cho nút ban đầu
        self.parent.btnSaveLight.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveLight", "#A4A4A4")
        self.parent.btnParameterDefaultLight.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultLight", "#A4A4A4")
        self.parent.btnTry.setEnabled(False)
        self.SetStyleSheetForbtn("btnTry", "#A4A4A4")
        self.parent.btnSaveCounter1.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCounter1", "#A4A4A4")
        self.parent.btnParameterConfirmation1.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterConfirmation1", "#A4A4A4")
        #Hiển thị tên sản phẩm từ lbProductName1
        #Kết nối chọn sản phẩm
        self.updateProductName(self.parent.lbProductName1.text())
        self.parent.label_56.setText(self.parent.lbProductName1.text())
        #Cho phép điều chỉnh thông số đèn
        self.parent.btnModifyLight.clicked.connect(lambda: [self.LeditModify(True), self.parent.btnModifyLight.setEnabled(False), self.SetStyleSheetForbtn("btnModifyLight", "#A4A4A4") ,self.parent.btnSaveLight.setEnabled(True), self.SetStyleSheetForbtn("btnSaveLight", "#DF2026"), self.parent.btnParameterDefaultLight.setEnabled(True), self.SetStyleSheetForbtn("btnParameterDefaultLight", "#F68013"), self.Push_working_history("Điều chỉnh thông số đèn")])
        #Lưu thông số đèn
        self.parent.btnSaveLight.clicked.connect(self.SaveLightConfig)
        #Trả về thông số mặc định của đèn
        self.parent.btnParameterDefaultLight.clicked.connect(self.DefaultLightConfig)
        #Đếm số lần test vị trí
        self.parent.lbTestCounter.setText("0")
        self.ImageCounter = 1
        # self.TriggerCounterImage = QTimer()
        # self.TriggerCounterImage.timeout.connect(self.CountImage)
        # self.TriggerCounterImage.start(500)
        #Nhấn nút thử lại
        # self.parent.btnTry.clicked.connect(lambda: [self.parent.lbImageConfirm.clear(), self.parent.label_66.setText("Hãy đưa sản phẩm vào kiểm tra"), self.parent.btnTry.setEnabled(False), self.SetStyleSheetForbtn("btnTry", "#A4A4A4"), self.StartTrigger()]) 
        self.parent.btnTry.clicked.connect(lambda: [self.parent.lbImageConfirm.clear(), self.parent.label_66.setText("Hãy đưa sản phẩm vào kiểm tra"), self.parent.btnTry.setEnabled(False), self.SetStyleSheetForbtn("btnTry", "#A4A4A4"), self.Push_working_history("Nhấn nút thử lại vị trí chụp sản phẩm"), self.StartTrigger()])
        #btnParameterConfirmation1
        self.parent.btnModifyCounter1.clicked.connect(lambda:[self.parent.leditTriggerDelay.setEnabled(True), self.parent.btnModifyCounter1.setEnabled(False), self.SetStyleSheetForbtn("btnModifyCounter1", "#A4A4A4"), self.parent.btnSaveCounter1.setEnabled(True), self.SetStyleSheetForbtn("btnSaveCounter1", "#DF2026"), self.Push_working_history("Điều chỉnh thông số delay")])
        self.parent.btnSaveCounter1.clicked.connect(self.SaveCounterConfig)
        #Cho phép qua trang Dashboard
        self.AcceptingConfirmation()
        self.Time_Start = QtCore.QDateTime.currentDateTime()
        self.UpdateHistoryTime()

    #Thiết lập bar side cho giao diện    
    def ToggleMenu(self):
        if self.parent.widgetOpen.isHidden():
            self.parent.stackedWidget.setMinimumSize(QtCore.QSize(1415, 789))
            self.parent.stackedWidget.setMaximumSize(QtCore.QSize(1415, 789))
        elif self.parent.widgetClose.isHidden():
            self.parent.stackedWidget.setMinimumSize(QtCore.QSize(1325, 789))
            self.parent.stackedWidget.setMaximumSize(QtCore.QSize(1325, 789)) 
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
    #Cho phép điều chỉnh thông số đèn
    def LeditModify(self,command):
        self.parent.leditLight1.setEnabled(command)
        self.parent.leditLight2.setEnabled(command)
        self.parent.leditLight3.setEnabled(command)
        self.parent.leditLight4.setEnabled(command)
    #Lưu thông số đèn
    def SaveLightConfig(self):
        self.Push_working_history("Lưu thông số đèn")
        #Lấy text hiện tại của QLineEdit
        light1 = self.parent.leditLight1.text()
        light2 = self.parent.leditLight2.text()
        light3 = self.parent.leditLight3.text()
        light4 = self.parent.leditLight4.text()
        #Update vào database
        c = self.conn.cursor()
        c.execute("UPDATE Product SET LIGHT1 = ?, LIGHT2 = ?, LIGHT3 = ?, LIGHT4 = ? WHERE rowid = ?", (light1, light2, light3, light4, self.RowId[0][0]))
        self.conn.commit()
        #Cho chép bấm nút Modify
        self.parent.btnModifyLight.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyLight", "#33D909")
        #Tắt nút khả năng nhấn của btnSaveLight
        self.parent.btnSaveLight.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveLight", "#A4A4A4")
        #Tắt nút khả năng nhấn của btnParameterDefaultLight
        self.parent.btnParameterDefaultLight.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultLight", "#A4A4A4")
    #Lấy thông số mặc định của đèn
    def DefaultLightConfig(self):
        self.Push_working_history("Trả về thông số mặc định của đèn")
        c = self.conn.cursor()
        #Lấy dữ liệu từ Light1Default Database
        Light1Default = c.execute("SELECT LIGHT1 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditLight1.setText(str(Light1Default[0]))
        #Lấy dữ liệu từ Light2Default Database
        Light2Default = c.execute("SELECT LIGHT2 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditLight2.setText(str(Light2Default[0]))
        #Lấy dữ liệu từ Light3Default Database
        Light3Default = c.execute("SELECT LIGHT3 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditLight3.setText(str(Light3Default[0]))
        #Lấy dữ liệu từ Light4Default Database
        Light4Default = c.execute("SELECT LIGHT4 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditLight4.setText(str(Light4Default[0]))
        #Cho chép bấm nút Modify
        self.parent.btnModifyLight.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyLight", "#33D909")
        #Tắt nút khả năng nhấn của btnSaveLight
        self.parent.btnSaveLight.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveLight", "#A4A4A4")
        #Tắt nút khả năng nhấn của btnParameterDefaultLight
        self.parent.btnParameterDefaultLight.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultLight", "#A4A4A4")
    #Cập nhật tên sản phẩm
    def updateProductName(self, text):        
        self.parent.label_56.setText(text)  # Cập nhật label 
        #Lấy thông số từ database
        c = self.conn.cursor()
        self.RowId = c.execute("SELECT rowid FROM Product WHERE ProductName = ?", (text,)).fetchall()
        #Hiện thị thông số  đèn 1
        self.Light1 = c.execute("SELECT LIGHT1 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditLight1.setText(str(self.Light1[0]))
        #Hiện thị thông số  đèn 2
        self.Light2 = c.execute("SELECT LIGHT2 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditLight2.setText(str(self.Light2[0]))
        #Hiện thị thông số  đèn 3
        self.Light3 = c.execute("SELECT LIGHT3 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditLight3.setText(str(self.Light3[0]))
        #Hiện thị thông số  đèn 4
        self.Light4 = c.execute("SELECT LIGHT4 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditLight4.setText(str(self.Light4[0]))
        #Hiển thị thông số delay
        self.Delay = c.execute("SELECT TriggerDelay FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditTriggerDelay.setText(str(self.Delay[0]))
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
                    print("Delay:", self.Delay[0])
                    time.sleep(self.Delay[0])
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
                    scaled_pixmap = pixmap.scaled(900, 640, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.parent.lbImageConfirm.setPixmap(scaled_pixmap)
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

    #Khi nhấn nút btnTry và ImageCounter > 0
    def StartTrigger(self):
        if self.ImageCounter > 0:
            self.TriggerTimerConfirm.start(10)  # Bắt đầu timer mỗi 500ms
            self.TriggerCounterImage.start(500)
            print("Trigger đang chạy...")

        else:
            print("Không thể chạy trigger, Test Counter = 0")
    #Đếm số lần hiển thị hình ảnh
    def CountImage(self):
        #Kiểm tra lbImageConfirm có đang chứa hình ảnh không
        pixmap = self.parent.lbImageConfirm.pixmap()
        if pixmap and not pixmap.isNull():
            self.ImageCounter += 1
            self.parent.lbTestCounter.setText(str(self.ImageCounter))
            self.parent.label_66.setText("Đã hiển thị hình ảnh")
            self.parent.btnTry.setEnabled(True)
            self.SetStyleSheetForbtn("btnTry", "#F68013")
            self.parent.btnParameterConfirmation1.setEnabled(True)
            self.SetStyleSheetForbtn("btnParameterConfirmation1", "#3D7AEF")
            self.TriggerTimerConfirm.stop()
            self.TriggerCounterImage.stop()
        else:
            self.parent.label_66.setText("Hãy đưa sản phẩm vào kiểm tra")
            self.parent.btnTry.setEnabled(False)
            self.SetStyleSheetForbtn("btnTry", "#A4A4A4")
            self.TriggerTimerConfirm.start(10)       
    #Xác nhận hoàn tất để chuyển hướng đến trang Dashboard
    def AcceptingConfirmation(self):
        if self.ImageCounter != 0:
            self.parent.btnParameterConfirmation1.setEnabled(True)
            self.SetStyleSheetForbtn("btnParameterConfirmation1", "#3D7AEF")
    #Lưu thông số delay
    def SaveCounterConfig(self):
        self.Push_working_history("Lưu thông số delay")
        # #Lấy text hiện tại của QLineEdit
        # TriggerDelay = float(self.parent.leditTriggerDelay.text())
        # Lấy text hiện tại của QLineEdit
        self.TriggerDelay = float(self.parent.leditTriggerDelay.text())
        #Update vào database
        c = self.conn.cursor()
        c.execute("UPDATE Product SET TriggerDelay = ? WHERE rowid = ?", (self.TriggerDelay, self.RowId[0][0]))
        self.conn.commit()
        #Cho chép bấm nút Modify
        self.parent.btnModifyCounter1.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyCounter1", "#33D909")
        #Tắt nút khả năng nhấn của btnSaveLight
        self.parent.btnSaveCounter1.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCounter1", "#A4A4A4")
        self.Delay = c.execute("SELECT TriggerDelay FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditTriggerDelay.setText(str(self.Delay[0]))
  
    def GetNextFilename(self):
        # Tìm số thứ tự tệp cuối cùng trong thư mục
        existing_files = sorted(
            [f for f in os.listdir(self.image_directory) if f.startswith("IMG_") and f.endswith(".bmp")]
        )
        
        if existing_files:
            # Lấy số thứ tự của tệp cuối cùng và tăng lên 1
            last_file = existing_files[-1]
            last_number = int(last_file[4:8])  # Lấy số từ "IMG_0001.bmp"
            next_number = (last_number + 1) % 10000  # Giới hạn từ 0000 đến 9999
        else:
            next_number = 1

        return os.path.join(self.image_directory, f"IMG_{next_number:04d}.bmp")   
    #Reset trang
    def InitialPage(self):
        # self.trigger = PageInitialBackend.Camera.f.TriggerSoftware  # Initialize trigger to None
        self.processing = False  # Trạng thái xử lý hình ảnh
        self.last_trigger_state = 0
        # self.TriggerTimerConfirm = QTimer()
        # self.TriggerTimerConfirm.timeout.connect(self.TriggerImage)
        self.parent.btnParameterConfirmation1.clicked.connect(lambda: [self.open_confirm_page(), self.ToggleMenu(), self.Push_working_history("Xác nhận hoàn tất kiểm tra vị trí chụp sản phẩm")])
        self.triggered = None
        self.image_directory = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceImages1"
        self.Time_Start = None
        self.Delay = []
        self.LeditModify(False)
        self.parent.leditTriggerDelay.setEnabled(False)
        #Set style cho nút ban đầu
        self.parent.btnSaveLight.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveLight", "#A4A4A4")
        self.parent.btnParameterDefaultLight.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultLight", "#A4A4A4")
        self.parent.btnTry.setEnabled(False)
        self.SetStyleSheetForbtn("btnTry", "#A4A4A4")
        self.parent.btnSaveCounter1.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCounter1", "#A4A4A4")
        self.parent.btnParameterConfirmation1.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterConfirmation1", "#A4A4A4")
        self.updateProductName(self.parent.lbProductName1.text())
        self.parent.label_56.setText(self.parent.lbProductName1.text())
        #Đếm số lần test vị trí
        self.parent.lbTestCounter.setText("0")
        self.ImageCounter = 1
        # self.TriggerCounterImage = QTimer()
        # self.TriggerCounterImage.timeout.connect(self.CountImage)
        # self.TriggerCounterImage.start(500)
        #Cho phép qua trang Dashboard
        self.AcceptingConfirmation()
        self.Time_Start = QtCore.QDateTime.currentDateTime()
        self.UpdateHistoryTime()

    def set_confirm_page1(self, confirm_page):
        self.confirm_page = confirm_page

    def open_confirm_page(self):
        if self.confirm_page:
            self.confirm_page.initializePage()  # Gọi lại như lần đầu
        self.parent.stackedWidget.setCurrentWidget(self.parent.page_Dashboard)

    def UpdateHistoryTime(self):
        #Lưu vào database
        c = self.conn.cursor()
        c.execute("INSERT INTO ProductHistory (ProductName, StartTime) VALUES (?, ?)", (self.parent.lbProductName1.text(), self.Time_Start.toString("yyyy-MM-dd hh:mm:ss")))
        self.conn.commit()

    def Push_working_history(self, action_name: str):
        action_time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        c = self.conn.cursor()
        #Lưu vào database
        c.execute("INSERT INTO WorkingHistory (FullName, Duty, ActionName, ActionTime) VALUES (?, ?, ?, ?)",
                (self.initial.FullName[0], self.initial.Duty[0], action_name, action_time))
        
        self.conn.commit()