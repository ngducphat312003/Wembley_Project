# from MainUI1 import Ui_MainWindow
# import neoapi
# from PyQt6 import QtCore
# from page_Initial import PageInitialBackend

# class PageParameterBackend():
#     trigger = None
#     def __init__(self, main: Ui_MainWindow, conn, initial: PageInitialBackend):
#         #Kết nối với main.py và Database
#         self.parent = main
#         self.conn = conn
#         self.initial = initial
#         #Không cho phép điều chỉnh thông số camera và đếm sản phẩm ban đầu
#         self.ModifyCamera(False)
#         self.ModifyCounter(False)   
#         #Setup các nút ban đầu
#         self.parent.btnDashboard.setEnabled(False)
#         self.parent.btnDashboard1.setEnabled(False)
#         self.parent.btnParameter.setEnabled(True)
#         self.parent.btnParameter1.setEnabled(True)
#         self.parent.btnModifyCam.setEnabled(False)
#         self.SetStyleSheetForbtn("btnModifyCam", "#A4A4A4")
#         self.parent.btnSaveCam.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveCam", "#A4A4A4")
#         self.parent.btnParameterDefaultCam.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultCam", "#A4A4A4")
#         self.parent.btnModifyCounter.setEnabled(False)
#         self.SetStyleSheetForbtn("btnModifyCounter", "#A4A4A4")
#         self.parent.btnSaveCounter.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveCounter", "#A4A4A4")
#         self.parent.btnParameterDefaultCounter.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultCounter", "#A4A4A4")
#         self.parent.btnParameterConfirmation.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterConfirmation", "#A4A4A4")
#         # Kết nối combobox cbProductSeclection
#         self.ProductSelection()
#         #Xác nhận thông số để qua trang page_Parameter_ConfimDelay
#         self.parent.btnParameterConfirmation.clicked.connect((lambda: [self.open_confirm_page(), self.ToggleMenu(), self.SetupCameraForTrigger(), self.Push_working_history("Xác nhận thông số")]))
#         # self.parent.btnParameterConfirmation.clicked.connect((lambda: [self.open_confirm_page(), self.ToggleMenu()]))
        
#         #Cho phép điều chỉnh thông số camera
#         self.parent.btnModifyCam.clicked.connect(lambda: [self.ModifyCamera(True), self.SetStyleSheetForbtn("btnModifyCam", "#A4A4A4"), self.parent.btnModifyCam.setEnabled(False), self.SetStyleSheetForbtn("btnSaveCam", "#DF2026"), self.parent.btnSaveCam.setEnabled(True), self.SetStyleSheetForbtn("btnParameterDefaultCam", "#F68013"), self.parent.btnParameterDefaultCam.setEnabled(True), self.Push_working_history("Điều chỉnh thông số camera")])
#         #Lưu thông số camera
#         self.parent.btnSaveCam.clicked.connect(self.SaveCameraConfig)
#         #Trả về thông số mặc định của camera
#         self.parent.btnParameterDefaultCam.clicked.connect(self.CameraDefault)
#         #Cho phép điều chỉnh thông số đếm sản phẩm
#         self.parent.btnModifyCounter.clicked.connect(lambda: [self.ModifyCounter(True), self.SetStyleSheetForbtn("btnModifyCounter", "#A4A4A4"), self.parent.btnModifyCounter.setEnabled(False), self.SetStyleSheetForbtn("btnSaveCounter", "#DF2026"), self.parent.btnSaveCounter.setEnabled(True), self.SetStyleSheetForbtn("btnParameterDefaultCounter", "#F68013"), self.parent.btnParameterDefaultCounter.setEnabled(True), self.Push_working_history("Điều chỉnh thông số đếm sản phẩm")])
#         #Lưu thông số đếm sản phẩm
#         self.parent.btnSaveCounter.clicked.connect(self.SaveCounterConfig)
#         #Trả về thông số mặc định của đếm sản phẩm
#         self.parent.btnParameterDefaultCounter.clicked.connect(self.CounterDefault)
#         #Hiển thị tên camera
#         self.parent.lbCameraName.setText(PageInitialBackend.CameraName) 
#         self.confirm_page = None
#     #Kết nối item cho combobox cbProductSeclection
#     def ProductSelection(self):
#         #Kết nối item từ Product Database
#         c = self.conn.cursor()
#         #Lấy tên sản phẩm từ Product Database
#         c.execute("SELECT ProductName FROM Product")
#         result = c.fetchall()
#         for row in result:
#             self.parent.cbProductSelection.addItem(row[0])
#         #Kết nối chọn sản phẩm
#         self.parent.cbProductSelection.currentTextChanged.connect(self.updateProductName)
#     #Cập nhật tên sản phẩm
#     def updateProductName(self, text):
#         #Cho phép điều chỉnh thông số camera và đếm sản phẩm
#         self.parent.btnModifyCam.setEnabled(True)
#         self.SetStyleSheetForbtn("btnModifyCam", "#33D909")
#         self.parent.btnModifyCounter.setEnabled(True)
#         self.SetStyleSheetForbtn("btnModifyCounter", "#33D909")
#         self.parent.btnParameterConfirmation.setEnabled(True)
#         self.SetStyleSheetForbtn("btnParameterConfirmation", "#3D7AEF")
#         """Cập nhật nhãn khi chọn sản phẩm"""
#         self.parent.lbProductName1.setText(text)  # Cập nhật label 
#         self.Push_working_history("Chọn sản phẩm: " + text) 

#         #Lấy rowid từ Product Database
#         c=self.conn.cursor()
#         self.RowId = c.execute("SELECT rowid FROM Product WHERE ProductName = ?", (text,)).fetchall()
#         #Hiển thị ExposureTime từ Product Database
#         self.ExposureTime = c.execute("SELECT ExposureTime FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditExposureTime.setText(str(self.ExposureTime[0]))
#         #Hiển thị Width từ Product Database
#         self.Width = c.execute("SELECT Width FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditWidth.setText(str(self.Width[0]))
#         #Hiển thị Height từ Product Database
#         self.Height = c.execute("SELECT Height FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditHeight.setText(str(self.Height[0]))
#         #Hiển thị OffsetX từ Product Database
#         self.OffsetX = c.execute("SELECT OffsetX FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditOffsetX.setText(str(self.OffsetX[0]))
#         #Hiển thị OffsetY từ Product Database
#         self.OffsetY = c.execute("SELECT OffsetY FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditOffsetY.setText(str(self.OffsetY[0]))
#         #Hiển thị TriggerDelay từ Product Database
#         self.TriggerDelay = c.execute("SELECT TriggerDelay FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditTriggerDelay_2.setText(str(self.TriggerDelay[0]))
#         #Hiển thị Dp từ Product Database
#         self.Dp = c.execute("SELECT Dp FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditDp.setText(str(self.Dp[0]))
#         #Hiển thị MinDist từ Product Database
#         self.MinDist = c.execute("SELECT minDist FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditMinDist.setText(str(self.MinDist[0]))
#         #Hiển thị Param1 từ Product Database
#         self.Param1 = c.execute("SELECT Param1 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditParam1.setText(str(self.Param1[0]))
#         #Hiển thị Param2 từ Product Database
#         self.Param2 = c.execute("SELECT Param2 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditParam2.setText(str(self.Param2[0]))
#         #Hiển thị Minradius từ Product Database
#         self.Minradius = c.execute("SELECT Minradius FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditMinradius.setText(str(self.Minradius[0]))
#         #Hiển thị Maxradius từ Product Database
#         self.Maxradius = c.execute("SELECT Maxradius FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditMaxradius.setText(str(self.Maxradius[0]))
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
#     #Cho phép điều chỉnh thông số camera
#     def ModifyCamera(self,command):
#         #Cho phép điều chỉnh LineEdit
#         self.parent.leditExposureTime.setEnabled(command)
#         self.parent.leditWidth.setEnabled(command)
#         self.parent.leditHeight.setEnabled(command)
#         self.parent.leditOffsetX.setEnabled(command)
#         self.parent.leditOffsetY.setEnabled(command)
#         self.parent.leditTriggerDelay_2.setEnabled(command)
#         #Tắt nút khả năng nhấn của btnSaveCam
#         self.parent.btnSaveCam.setEnabled(command)
#         #Tắt nút khả năng nhấn của btnParameterDefaultCam
#         self.parent.btnParameterDefaultCam.setEnabled(command)
#     #Lưu thông số camera
#     def SaveCameraConfig(self):
#         self.Push_working_history("Lưu thông số camera")

#         #Lấy text hiện tại của QLineEdit
#         ExposureTimeEdit = self.parent.leditExposureTime.text()
#         WidthEdit = self.parent.leditWidth.text()
#         HeightEdit = self.parent.leditHeight.text()
#         OffsetXEdit = self.parent.leditOffsetX.text()
#         OffsetYEdit = self.parent.leditOffsetY.text()
#         TriggerDelayEdit = self.parent.leditTriggerDelay_2.text()
#         #Update thông số camera vào Product Database
#         c = self.conn.cursor()
#         c.execute("UPDATE Product SET ExposureTime = ?, Width = ?, Height = ?, OffsetX = ?, OffsetY = ?, TriggerDelay = ? WHERE rowid = ?", (ExposureTimeEdit, WidthEdit, HeightEdit, OffsetXEdit, OffsetYEdit, TriggerDelayEdit, self.RowId[0][0]))
#         self.conn.commit()
#         #Cho chép bấm nút Modify
#         self.parent.btnModifyCam.setEnabled(True)
#         self.SetStyleSheetForbtn("btnModifyCam", "#33D909")
#         #Tắt nút khả năng nhấn của btnSaveCam
#         self.parent.btnSaveCam.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveCam", "#A4A4A4")
#         #Tắt nút khả năng nhấn của btnParameterDefaultCam
#         self.parent.btnParameterDefaultCam.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultCam", "#A4A4A4")
#         #Tắt khả năng nhấn nút điều chỉnh
#         self.ModifyCamera(False)
#     #Trả về thông số mặc định của camera
#     def CameraDefault(self): 
#         self.Push_working_history("Trả về thông số mặc định của camera")
#         c = self.conn.cursor()
#         #Lấy dữ liệu từ ExposureTimeDefault Database
#         self.ExposureTimeDefault = c.execute("SELECT ExposureTime FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditExposureTime.setText(str(self.ExposureTimeDefault[0]))
#         #Lấy dữ liệu từ WidthDefault Database
#         self.WidthDefault = c.execute("SELECT Width FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditWidth.setText(str(self.WidthDefault[0]))
#         #Lấy dữ liệu từ HeightDefault Database
#         self.HeightDefault = c.execute("SELECT Height FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditHeight.setText(str(self.HeightDefault[0]))
#         #Lấy dữ liệu từ OffsetXDefault Database
#         self.OffsetXDefault = c.execute("SELECT OffsetX FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditOffsetX.setText(str(self.OffsetXDefault[0]))
#         #Lấy dữ liệu từ OffsetYDefault Database
#         self.OffsetYDefault = c.execute("SELECT OffsetY FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditOffsetY.setText(str(self.OffsetYDefault[0]))
#         #Lấy dữ liệu từ TriggerDelayDefault Database
#         self.TriggerDelayDefault = c.execute("SELECT TriggerDelay FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditTriggerDelay_2.setText(str(self.TriggerDelayDefault[0]))
#         #Cho phép bấm nút Modify
#         self.parent.btnModifyCam.setEnabled(True)
#         self.SetStyleSheetForbtn("btnModifyCam", "#33D909")
#         #Tắt nút khả năng nhấn của btnSaveCam
#         self.parent.btnSaveCam.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveCam", "#A4A4A4")
#         #Tắt nút khả năng nhấn của btnParameterDefaultCam
#         self.parent.btnParameterDefaultCam.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultCam", "#A4A4A4")
#         self.ModifyCamera(False)
#     #Cho phép điều chỉnh thông số đếm sản phẩmFailed to get PLC variable
#     def ModifyCounter(self,command):
#         #Cho phép điều chỉnh LineEdit
#         self.parent.leditDp.setEnabled(command)
#         self.parent.leditMinDist.setEnabled(command)
#         self.parent.leditParam1.setEnabled(command)
#         self.parent.leditParam2.setEnabled(command)
#         self.parent.leditMinradius.setEnabled(command)
#         self.parent.leditMaxradius.setEnabled(command)
#         #Tắt nút khả năng nhấn của btnSaveCounter
#         self.parent.btnSaveCounter.setEnabled(command)
#         #Tắt nút khả năng nhấn của btnParameterDefaultCounter
#         self.parent.btnParameterDefaultCounter.setEnabled(command)
#     #Lưu thông số đếm sản phẩm
#     def SaveCounterConfig(self):
#         # self.Push_working_history("Lưu thông số đếm sản phẩm")
#         #Lấy text hiện tại của QLineEdit
#         DpEdit = self.parent.leditDp.text()
#         MinDistEdit = self.parent.leditMinDist.text()
#         Param1Edit = self.parent.leditParam1.text()
#         Param2Edit = self.parent.leditParam2.text()
#         MinradiusEdit = self.parent.leditMinradius.text()
#         MaxradiusEdit = self.parent.leditMaxradius.text()
#         #Update thông số đếm sản phẩm vào Product Database
#         c = self.conn.cursor()
#         c.execute("UPDATE Product SET Dp = ?, minDist = ?, Param1 = ?, Param2 = ?, Minradius = ?, Maxradius = ? WHERE rowid = ?", (DpEdit, MinDistEdit, Param1Edit, Param2Edit, MinradiusEdit, MaxradiusEdit, self.RowId[0][0]))
#         self.conn.commit()
#         #Cho chép bấm nút Modify
#         self.parent.btnModifyCounter.setEnabled(True)
#         self.SetStyleSheetForbtn("btnModifyCounter", "#33D909")
#         #Tắt nút khả năng nhấn của btnSaveCounter
#         self.parent.btnSaveCounter.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveCounter", "#A4A4A4")
#         #Tắt nút khả năng nhấn của btnParameterDefaultCounter
#         self.parent.btnParameterDefaultCounter.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultCounter", "#A4A4A4")
#         self.ModifyCounter(False)
#     #Trả về thông số mặc định của đếm sản phẩm
#     def CounterDefault(self):
#         # self.Push_working_history("Trả về thông số mặc định của đếm sản phẩm")
#         c = self.conn.cursor()
#         #Lấy dữ liệu từ DpDefault Database
#         self.DpDefault = c.execute("SELECT Dp FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditDp.setText(str(self.DpDefault[0]))
#         #Lấy dữ liệu từ MinDistDefault Database
#         self.MinDistDefault = c.execute("SELECT minDist FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditMinDist.setText(str(self.MinDistDefault[0]))
#         #Lấy dữ liệu từ Param1Default Database
#         self.Param1Default = c.execute("SELECT Param1 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditParam1.setText(str(self.Param1Default[0]))
#         #Lấy dữ liệu từ Param2Default Database
#         self.Param2Default = c.execute("SELECT Param2 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditParam2.setText(str(self.Param2Default[0]))
#         #Lấy dữ liệu từ MinradiusDefault Database
#         self.MinradiusDefault = c.execute("SELECT Minradius FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditMinradius.setText(str(self.MinradiusDefault[0]))
#         #Lấy dữ liệu từ MaxradiusDefault Database
#         self.MaxradiusDefault = c.execute("SELECT Maxradius FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.parent.leditMaxradius.setText(str(self.MaxradiusDefault[0]))
#         #Cho phép bấm nút Modify
#         self.parent.btnModifyCounter.setEnabled(True)
#         self.SetStyleSheetForbtn("btnModifyCounter", "#33D909")
#         #Tắt nút khả năng nhấn của btnSaveCounter
#         self.parent.btnSaveCounter.setEnabled(False)
#         self.SetStyleSheetForbtn("btnSaveCounter", "#A4A4A4")
#         #Tắt nút khả năng nhấn của btnParameterDefaultCounter
#         self.parent.btnParameterDefaultCounter.setEnabled(False)
#         self.SetStyleSheetForbtn("btnParameterDefaultCounter", "#A4A4A4")
#         self.ModifyCounter(False)
#     #Thiết lập thông số camera cho quá trình trigger
#     def SetupCameraForTrigger(self):
#         #Lấy thông số camera từ Database
#         c = self.conn.cursor()
#         self.ExposureTime = c.execute("SELECT ExposureTime FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.Width = c.execute("SELECT Width FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.Height = c.execute("SELECT Height FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.OffsetX = c.execute("SELECT OffsetX FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
#         self.OffsetY = c.execute("SELECT OffsetY FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()

#         self.initial.Camera.f.ExposureTime.Set(self.ExposureTime[0])
#         print("Đặt thời gian phơi sáng PARA: ", self.ExposureTime[0])
#         self.initial.Camera.f.Width.Set(self.Width[0])
#         self.initial.Camera.f.Height.Set(self.Height[0])
#         self.initial.Camera.f.OffsetX.Set(self.OffsetX[0])
#         self.initial.Camera.f.OffsetY.Set(self.OffsetY[0])
#         self.initial.Camera.f.Gain.Set(1)
#         self.initial.Camera.f.PixelFormat.Set(neoapi.PixelFormat_BayerRG8)
#         self.initial.Camera.f.BalanceWhiteAuto = neoapi.BalanceWhiteAuto_Off
#         self.initial.Camera.f.TriggerMode.value = neoapi.TriggerMode_On
#         PageParameterBackend.trigger = self.initial.Camera.f.TriggerSoftware
#         if self.initial.Camera.HasFeature("SharpeningEnable"):
#             self.initial.Camera.SetFeature("SharpeningEnable", False)
#         if self.initial.Camera.HasFeature("NoiseReductionEnable"):
#             self.initial.Camera.SetFeature("NoiseReductionEnable", False)
#         #Bật chế độ use optimal buffer size
#         if self.initial.Camera.HasFeature("UseOptimalBufferSize"):
#             self.initial.Camera.SetFeature("UseOptimalBufferSize", True)
        
#     def set_confirm_page(self, confirm_page):
#         self.confirm_page = confirm_page

#     def open_confirm_page(self):
#         print("self.confirm_page", self.confirm_page)
#         if self.confirm_page:
#             print("open_confirm_page")
#             self.confirm_page.InitialPage()  # Gọi lại như lần đầu
#         self.parent.stackedWidget.setCurrentWidget(self.parent.page_Parameter_ConfimDelay)
        
#     def Push_working_history(self, action_name: str):
#         action_time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
#         c = self.conn.cursor()
#         #Lưu vào database
#         c.execute("INSERT INTO WorkingHistory (FullName, Duty, ActionName, ActionTime) VALUES (?, ?, ?, ?)",
#                 (self.initial.FullName[0], self.initial.Duty[0], action_name, action_time))
        
#         self.conn.commit()
# # #################################################################

from MainUI1 import Ui_MainWindow
import neoapi
from PyQt6 import QtCore
from page_Initial import PageInitialBackend

class PageParameterBackend():
    trigger = None
    def __init__(self, main: Ui_MainWindow, conn, initial: PageInitialBackend):
        #Kết nối với main.py và Database
        self.parent = main
        self.conn = conn
        self.initial = initial
        #Không cho phép điều chỉnh thông số camera và đếm sản phẩm ban đầu
        self.ModifyCamera(False)
        self.ModifyCounter(False)   
        self.parent.btnDashboard.setEnabled(False)
        self.parent.btnDashboard1.setEnabled(False)
        self.parent.btnParameter.setEnabled(True)
        self.parent.btnParameter1.setEnabled(True)
        #Setup các nút ban đầu
        self.parent.btnModifyCam.setEnabled(False)
        self.SetStyleSheetForbtn("btnModifyCam", "#A4A4A4")
        self.parent.btnSaveCam.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCam", "#A4A4A4")
        self.parent.btnParameterDefaultCam.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultCam", "#A4A4A4")
        self.parent.btnModifyCounter.setEnabled(False)
        self.SetStyleSheetForbtn("btnModifyCounter", "#A4A4A4")
        self.parent.btnSaveCounter.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCounter", "#A4A4A4")
        self.parent.btnParameterDefaultCounter.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultCounter", "#A4A4A4")
        self.parent.btnParameterConfirmation.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterConfirmation", "#A4A4A4")
        # Kết nối combobox cbProductSeclection
        self.ProductSelection()
        #Xác nhận thông số để qua trang page_Parameter_ConfimDelay
        # self.parent.btnParameterConfirmation.clicked.connect((lambda: [self.parent.stackedWidget.setCurrentWidget(self.parent.page_Parameter_ConfimDelay), self.ToggleMenu()]))
        # self.parent.btnParameterConfirmation.clicked.connect((lambda: [self.open_confirm_page(), self.ToggleMenu(), self.SetupCameraForTrigger()]))
        self.parent.btnParameterConfirmation.clicked.connect((lambda: [self.open_confirm_page(), self.ToggleMenu(), self.Push_working_history("Xác nhận thông số")]))
        
        #Cho phép điều chỉnh thông số camera
        self.parent.btnModifyCam.clicked.connect(lambda: [self.ModifyCamera(True), self.SetStyleSheetForbtn("btnModifyCam", "#A4A4A4"), self.parent.btnModifyCam.setEnabled(False), self.SetStyleSheetForbtn("btnSaveCam", "#DF2026"), self.parent.btnSaveCam.setEnabled(True), self.SetStyleSheetForbtn("btnParameterDefaultCam", "#F68013"), self.parent.btnParameterDefaultCam.setEnabled(True), self.Push_working_history("Điều chỉnh thông số camera")])
        #Lưu thông số camera
        self.parent.btnSaveCam.clicked.connect(self.SaveCameraConfig)
        #Trả về thông số mặc định của camera
        self.parent.btnParameterDefaultCam.clicked.connect(self.CameraDefault)
        #Cho phép điều chỉnh thông số đếm sản phẩm
        self.parent.btnModifyCounter.clicked.connect(lambda: [self.ModifyCounter(True), self.SetStyleSheetForbtn("btnModifyCounter", "#A4A4A4"), self.parent.btnModifyCounter.setEnabled(False), self.SetStyleSheetForbtn("btnSaveCounter", "#DF2026"), self.parent.btnSaveCounter.setEnabled(True), self.SetStyleSheetForbtn("btnParameterDefaultCounter", "#F68013"), self.parent.btnParameterDefaultCounter.setEnabled(True), self.Push_working_history("Điều chỉnh thông số đếm sản phẩm")])
        #Lưu thông số đếm sản phẩm
        self.parent.btnSaveCounter.clicked.connect(self.SaveCounterConfig)
        #Trả về thông số mặc định của đếm sản phẩm
        self.parent.btnParameterDefaultCounter.clicked.connect(self.CounterDefault)
        #Hiển thị tên camera
        # self.parent.lbCameraName.setText(self.initial.CameraName) 
        self.confirm_page = None
        

    #Kết nối item cho combobox cbProductSeclection
    def ProductSelection(self):
        #Kết nối item từ Product Database
        c = self.conn.cursor()
        #Lấy tên sản phẩm từ Product Database
        c.execute("SELECT ProductName FROM Product")
        result = c.fetchall()
        for row in result:
            self.parent.cbProductSelection.addItem(row[0])
        #Kết nối chọn sản phẩm
        self.parent.cbProductSelection.currentTextChanged.connect(self.updateProductName)
    #Cập nhật tên sản phẩm
    def updateProductName(self, text):
        #Cho phép điều chỉnh thông số camera và đếm sản phẩm
        self.parent.btnModifyCam.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyCam", "#33D909")
        self.parent.btnModifyCounter.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyCounter", "#33D909")
        self.parent.btnParameterConfirmation.setEnabled(True)
        self.SetStyleSheetForbtn("btnParameterConfirmation", "#3D7AEF")
        """Cập nhật nhãn khi chọn sản phẩm"""
        self.parent.lbProductName1.setText(text)  # Cập nhật label
        self.Push_working_history("Chọn sản phẩm: " + text) 
        #Lấy rowid từ Product Database
        c=self.conn.cursor()
        self.RowId = c.execute("SELECT rowid FROM Product WHERE ProductName = ?", (text,)).fetchall()
        #Hiển thị ExposureTime từ Product Database
        self.ExposureTime = c.execute("SELECT ExposureTime FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditExposureTime.setText(str(self.ExposureTime[0]))
        #Hiển thị Width từ Product Database
        self.Width = c.execute("SELECT Width FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditWidth.setText(str(self.Width[0]))
        #Hiển thị Height từ Product Database
        self.Height = c.execute("SELECT Height FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditHeight.setText(str(self.Height[0]))
        #Hiển thị OffsetX từ Product Database
        self.OffsetX = c.execute("SELECT OffsetX FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditOffsetX.setText(str(self.OffsetX[0]))
        #Hiển thị OffsetY từ Product Database
        self.OffsetY = c.execute("SELECT OffsetY FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditOffsetY.setText(str(self.OffsetY[0]))
        #Hiển thị TriggerDelay từ Product Database
        self.TriggerDelay = c.execute("SELECT TriggerDelay FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditTriggerDelay_2.setText(str(self.TriggerDelay[0]))
        #Hiển thị Dp từ Product Database
        self.Dp = c.execute("SELECT Dp FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditDp.setText(str(self.Dp[0]))
        #Hiển thị MinDist từ Product Database
        self.MinDist = c.execute("SELECT minDist FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditMinDist.setText(str(self.MinDist[0]))
        #Hiển thị Param1 từ Product Database
        self.Param1 = c.execute("SELECT Param1 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditParam1.setText(str(self.Param1[0]))
        #Hiển thị Param2 từ Product Database
        self.Param2 = c.execute("SELECT Param2 FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditParam2.setText(str(self.Param2[0]))
        #Hiển thị Minradius từ Product Database
        self.Minradius = c.execute("SELECT Minradius FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditMinradius.setText(str(self.Minradius[0]))
        #Hiển thị Maxradius từ Product Database
        self.Maxradius = c.execute("SELECT Maxradius FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditMaxradius.setText(str(self.Maxradius[0]))
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
    #Cho phép điều chỉnh thông số camera
    def ModifyCamera(self,command):
        #Cho phép điều chỉnh LineEdit
        self.parent.leditExposureTime.setEnabled(command)
        self.parent.leditWidth.setEnabled(command)
        self.parent.leditHeight.setEnabled(command)
        self.parent.leditOffsetX.setEnabled(command)
        self.parent.leditOffsetY.setEnabled(command)
        self.parent.leditTriggerDelay_2.setEnabled(command)
        #Tắt nút khả năng nhấn của btnSaveCam
        self.parent.btnSaveCam.setEnabled(command)
        #Tắt nút khả năng nhấn của btnParameterDefaultCam
        self.parent.btnParameterDefaultCam.setEnabled(command)
    #Lưu thông số camera
    def SaveCameraConfig(self):
        self.Push_working_history("Lưu thông số camera")
        #Lấy text hiện tại của QLineEdit
        ExposureTimeEdit = self.parent.leditExposureTime.text()
        WidthEdit = self.parent.leditWidth.text()
        HeightEdit = self.parent.leditHeight.text()
        OffsetXEdit = self.parent.leditOffsetX.text()
        OffsetYEdit = self.parent.leditOffsetY.text()
        TriggerDelayEdit = self.parent.leditTriggerDelay_2.text()
        #Update thông số camera vào Product Database
        c = self.conn.cursor()
        c.execute("UPDATE Product SET ExposureTime = ?, Width = ?, Height = ?, OffsetX = ?, OffsetY = ?, TriggerDelay = ? WHERE rowid = ?", (ExposureTimeEdit, WidthEdit, HeightEdit, OffsetXEdit, OffsetYEdit, TriggerDelayEdit, self.RowId[0][0]))
        self.conn.commit()
        #Cho chép bấm nút Modify
        self.parent.btnModifyCam.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyCam", "#33D909")
        #Tắt nút khả năng nhấn của btnSaveCam
        self.parent.btnSaveCam.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCam", "#A4A4A4")
        #Tắt nút khả năng nhấn của btnParameterDefaultCam
        self.parent.btnParameterDefaultCam.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultCam", "#A4A4A4")
        #Tắt khả năng nhấn nút điều chỉnh
        self.ModifyCamera(False)
    #Trả về thông số mặc định của camera
    def CameraDefault(self):        
        self.Push_working_history("Trả về thông số mặc định của camera")
        c = self.conn.cursor()
        #Lấy dữ liệu từ ExposureTimeDefault Database
        self.ExposureTimeDefault = c.execute("SELECT ExposureTime FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditExposureTime.setText(str(self.ExposureTimeDefault[0]))
        #Lấy dữ liệu từ WidthDefault Database
        self.WidthDefault = c.execute("SELECT Width FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditWidth.setText(str(self.WidthDefault[0]))
        #Lấy dữ liệu từ HeightDefault Database
        self.HeightDefault = c.execute("SELECT Height FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditHeight.setText(str(self.HeightDefault[0]))
        #Lấy dữ liệu từ OffsetXDefault Database
        self.OffsetXDefault = c.execute("SELECT OffsetX FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditOffsetX.setText(str(self.OffsetXDefault[0]))
        #Lấy dữ liệu từ OffsetYDefault Database
        self.OffsetYDefault = c.execute("SELECT OffsetY FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditOffsetY.setText(str(self.OffsetYDefault[0]))
        #Lấy dữ liệu từ TriggerDelayDefault Database
        self.TriggerDelayDefault = c.execute("SELECT TriggerDelay FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditTriggerDelay_2.setText(str(self.TriggerDelayDefault[0]))
        #Cho phép bấm nút Modify
        self.parent.btnModifyCam.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyCam", "#33D909")
        #Tắt nút khả năng nhấn của btnSaveCam
        self.parent.btnSaveCam.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCam", "#A4A4A4")
        #Tắt nút khả năng nhấn của btnParameterDefaultCam
        self.parent.btnParameterDefaultCam.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultCam", "#A4A4A4")
        self.ModifyCamera(False)
    #Cho phép điều chỉnh thông số đếm sản phẩmFailed to get PLC variable
    def ModifyCounter(self,command):
        #Cho phép điều chỉnh LineEdit
        self.parent.leditDp.setEnabled(command)
        self.parent.leditMinDist.setEnabled(command)
        self.parent.leditParam1.setEnabled(command)
        self.parent.leditParam2.setEnabled(command)
        self.parent.leditMinradius.setEnabled(command)
        self.parent.leditMaxradius.setEnabled(command)
        #Tắt nút khả năng nhấn của btnSaveCounter
        self.parent.btnSaveCounter.setEnabled(command)
        #Tắt nút khả năng nhấn của btnParameterDefaultCounter
        self.parent.btnParameterDefaultCounter.setEnabled(command)
    #Lưu thông số đếm sản phẩm
    def SaveCounterConfig(self):
        self.Push_working_history("Lưu thông số đếm sản phẩm")
        #Lấy text hiện tại của QLineEdit
        DpEdit = self.parent.leditDp.text()
        MinDistEdit = self.parent.leditMinDist.text()
        Param1Edit = self.parent.leditParam1.text()
        Param2Edit = self.parent.leditParam2.text()
        MinradiusEdit = self.parent.leditMinradius.text()
        MaxradiusEdit = self.parent.leditMaxradius.text()
        #Update thông số đếm sản phẩm vào Product Database
        c = self.conn.cursor()
        c.execute("UPDATE Product SET Dp = ?, minDist = ?, Param1 = ?, Param2 = ?, Minradius = ?, Maxradius = ? WHERE rowid = ?", (DpEdit, MinDistEdit, Param1Edit, Param2Edit, MinradiusEdit, MaxradiusEdit, self.RowId[0][0]))
        self.conn.commit()
        #Cho chép bấm nút Modify
        self.parent.btnModifyCounter.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyCounter", "#33D909")
        #Tắt nút khả năng nhấn của btnSaveCounter
        self.parent.btnSaveCounter.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCounter", "#A4A4A4")
        #Tắt nút khả năng nhấn của btnParameterDefaultCounter
        self.parent.btnParameterDefaultCounter.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultCounter", "#A4A4A4")
        self.ModifyCounter(False)
    #Trả về thông số mặc định của đếm sản phẩm
    def CounterDefault(self):
        self.Push_working_history("Trả về thông số mặc định của đếm sản phẩm")
        c = self.conn.cursor()
        #Lấy dữ liệu từ DpDefault Database
        self.DpDefault = c.execute("SELECT Dp FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditDp.setText(str(self.DpDefault[0]))
        #Lấy dữ liệu từ MinDistDefault Database
        self.MinDistDefault = c.execute("SELECT minDist FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditMinDist.setText(str(self.MinDistDefault[0]))
        #Lấy dữ liệu từ Param1Default Database
        self.Param1Default = c.execute("SELECT Param1 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditParam1.setText(str(self.Param1Default[0]))
        #Lấy dữ liệu từ Param2Default Database
        self.Param2Default = c.execute("SELECT Param2 FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditParam2.setText(str(self.Param2Default[0]))
        #Lấy dữ liệu từ MinradiusDefault Database
        self.MinradiusDefault = c.execute("SELECT Minradius FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditMinradius.setText(str(self.MinradiusDefault[0]))
        #Lấy dữ liệu từ MaxradiusDefault Database
        self.MaxradiusDefault = c.execute("SELECT Maxradius FROM ProductDefault WHERE rowid = ?", self.RowId[0]).fetchone()
        self.parent.leditMaxradius.setText(str(self.MaxradiusDefault[0]))
        #Cho phép bấm nút Modify
        self.parent.btnModifyCounter.setEnabled(True)
        self.SetStyleSheetForbtn("btnModifyCounter", "#33D909")
        #Tắt nút khả năng nhấn của btnSaveCounter
        self.parent.btnSaveCounter.setEnabled(False)
        self.SetStyleSheetForbtn("btnSaveCounter", "#A4A4A4")
        #Tắt nút khả năng nhấn của btnParameterDefaultCounter
        self.parent.btnParameterDefaultCounter.setEnabled(False)
        self.SetStyleSheetForbtn("btnParameterDefaultCounter", "#A4A4A4")
        self.ModifyCounter(False)
    #Thiết lập thông số camera cho quá trình trigger
    def SetupCameraForTrigger(self):
        #Lấy thông số camera từ Database
        c = self.conn.cursor()
        self.ExposureTime = c.execute("SELECT ExposureTime FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.Width = c.execute("SELECT Width FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.Height = c.execute("SELECT Height FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.OffsetX = c.execute("SELECT OffsetX FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()
        self.OffsetY = c.execute("SELECT OffsetY FROM Product WHERE rowid = ?", self.RowId[0]).fetchone()

        self.initial.Camera.f.ExposureTime.Set(self.ExposureTime[0])
        print("Đặt thời gian phơi sáng PARA: ", self.ExposureTime[0])
        self.initial.Camera.f.Width.Set(self.Width[0])
        self.initial.Camera.f.Height.Set(self.Height[0])
        self.initial.Camera.f.OffsetX.Set(self.OffsetX[0])
        self.initial.Camera.f.OffsetY.Set(self.OffsetY[0])
        self.initial.Camera.f.Gain.Set(1)
        self.initial.Camera.f.PixelFormat.Set(neoapi.PixelFormat_BayerRG8)
        self.initial.Camera.f.BalanceWhiteAuto = neoapi.BalanceWhiteAuto_Off
        self.initial.Camera.f.TriggerMode.value = neoapi.TriggerMode_On
        PageParameterBackend.trigger = self.initial.Camera.f.TriggerSoftware
        if self.initial.Camera.HasFeature("SharpeningEnable"):
            self.initial.Camera.SetFeature("SharpeningEnable", False)
        if self.initial.Camera.HasFeature("NoiseReductionEnable"):
            self.initial.Camera.SetFeature("NoiseReductionEnable", False)
        #Bật chế độ use optimal buffer size
        if self.initial.Camera.HasFeature("UseOptimalBufferSize"):
            self.initial.Camera.SetFeature("UseOptimalBufferSize", True)
        
    def set_confirm_page(self, confirm_page):
        self.confirm_page = confirm_page

    def open_confirm_page(self):
        if self.confirm_page:
            self.confirm_page.InitialPage()  # Gọi lại như lần đầu
        self.parent.stackedWidget.setCurrentWidget(self.parent.page_Parameter_ConfimDelay)

    def Push_working_history(self, action_name: str):
        action_time = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        c = self.conn.cursor()
        #Lưu vào database
        c.execute("INSERT INTO WorkingHistory (FullName, Duty, ActionName, ActionTime) VALUES (?, ?, ?, ?)",
                (self.initial.FullName[0], self.initial.Duty[0], action_name, action_time))
        
        self.conn.commit()

    