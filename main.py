from LoginPage import Ui_Login 
from MainUI1 import Ui_MainWindow

from page_Initial import PageInitialBackend
from page_Parameter import PageParameterBackend
from page_Parameter_ConfimDelay import PageParameterConfirmBackend
from page_Admin import AdminBackend
from page_Dashboard import DashboardBackend
from page_Configuration import ConfigurationBackend
from page_History import HistoryBackend

import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QGraphicsDropShadowEffect
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
import sys
import os, time
import bcrypt

class PermissionManager:
    def __init__(self, permission_string):
        self.permissions = set(permission_string)  # Eg: {'1', '2', '3'}

    def has_permission(self, code):
        return str(code) in self.permissions

class MainApp(QMainWindow, Ui_MainWindow):
    def __init__(self, conn, KeyPrimary, perm_manager):
        super().__init__()
        self.setupUi(self)
        self.conn = conn
        self.KeyPrimary = KeyPrimary
        self.perm_manager = perm_manager
        self.apply_permissions()
        #Hiển thị trang Initial khi chương trình chạy
        #self.stackedWidget.setCurrentWidget(self.page_Parameter_ConfimDelay)
        #self.stackedWidget.setCurrentWidget(self.page_Dashboard)
        self.stackedWidget.setCurrentWidget(self.page_Initial)
        self.page_button_map = {
            self.page_Initial: [self.btnInitial, self.btnInitial1],
            self.page_Parameter: [self.btnParameter, self.btnParameter1],  # Nhóm 1
            self.page_Parameter_ConfimDelay: [self.btnParameter, self.btnParameter1],  # Nhóm 1 (Giữ nguyên button)
            self.page_Dashboard: [self.btnDashboard, self.btnDashboard1],
            self.page_Configuration: [self.btnConfiguration, self.btnConfiguration1],
            self.page_History: [self.btnHistory, self.btnHistory1],
            self.page_Admin: [self.btnAdmin, self.btnAdmin1],
            }
        self.updateButtonStyles()
        self.stackedWidget.currentChanged.connect(self.updateButtonStyles)
        
        # Giả sử widgetOpen bắt đầu ở trạng thái ẩn
        self.widgetOpen.hide()  
        # Giả sử widgetClose bắt đầu ở trạng thái hiển thị
        self.widgetClose.show()  
        self.ToggleMenu()
        #Kết nối nút nhấn với hàm ToggleMenu
        self.btnLogo.pressed.connect(self.ToggleMenu)
        self.btnLogo1.pressed.connect(self.ToggleMenu)
        #Kết nối các nút nhấn với các trang
        #page_Initial
        self.page_initial = PageInitialBackend(self, self.conn, self.KeyPrimary)
        self.btnInitial.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_Initial), self.ToggleMenu(), self.btnParameter.setEnabled(False), self.btnParameter1.setEnabled(False), self.btnDashboard.setEnabled(False), self.btnDashboard1.setEnabled(False)])
        self.btnInitial1.clicked.connect(lambda: [self.stackedWidget.setCurrentWidget(self.page_Initial), self.ToggleMenu(), self.btnParameter.setEnabled(False), self.btnParameter1.setEnabled(False), self.btnDashboard.setEnabled(False), self.btnDashboard1.setEnabled(False)])
        #Nút nhấn Logout
        self.btnLogout.clicked.connect(self.Logout)
        #page_Parameter
        self.page_parameter = None  
        self.btnParameter.clicked.connect(self.openParameterPage)
        self.btnParameter1.clicked.connect(self.openParameterPage)
        self.stackedWidget.currentChanged.connect(self.checkParameterPage)
        #page_Parameter_ConfimDelay
        self.page_parameter_confirm = None
        self.stackedWidget.currentChanged.connect(self.checkParameterConfirmPage)
        #page_Dashboard
        self.page_dashboard = None
        self.btnDashboard.clicked.connect(self.openDashboardPage)
        self.btnDashboard1.clicked.connect(self.openDashboardPage)
        self.stackedWidget.currentChanged.connect(self.checkDashboardPage)
        #Hiển thị thời gian
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.ShowTime)  # Gọi ShowTime mỗi giây
        self.timer.start(1000)  # Cập nhật mỗi 1000ms (1 giây)
        self.ShowTime()
        #Không được phép nhấn dtDayCurrent
        self.dtDayCurrent.setDisabled(True)
        #page_History
        self.page_history = None
        self.btnHistory.clicked.connect(self.openHistoryPage)
        self.btnHistory1.clicked.connect(self.openHistoryPage)
        self.stackedWidget.currentChanged.connect(self.checkHistoryPage)
        #page_Admin
        self.page_admin = None
        self.btnAdmin.clicked.connect(self.openAdminPage)
        self.btnAdmin1.clicked.connect(self.openAdminPage)
        self.stackedWidget.currentChanged.connect(self.checkAdminPage)
        #page_Configuration
        self.page_configuration = None
        self.btnConfiguration.clicked.connect(self.openConfigurationPage)
        self.btnConfiguration1.clicked.connect(self.openConfigurationPage)
        self.stackedWidget.currentChanged.connect(self.checkConfigurationPage)
    #Thiết lập bar side cho giao diện    
    def ToggleMenu(self):
        if self.widgetOpen.isHidden():
            self.stackedWidget.setMinimumSize(QtCore.QSize(1415, 789))
            self.stackedWidget.setMaximumSize(QtCore.QSize(1415, 789))
        elif self.widgetClose.isHidden():
            self.stackedWidget.setMinimumSize(QtCore.QSize(1325, 789))
            self.stackedWidget.setMaximumSize(QtCore.QSize(1325, 789))
    #Backend cho trang Initial
    #Thiết lập chức năng Logout cho 
    def Logout(self):
        self.close()
        #PageInitialBackend.camera.Disconnect()
        #PageInitialBackend.camera_connected = False
        self.window = MainWindow()
        self.window.show()
    #Hiển thị thời gian realtime dạng giờ:phút:giây dtDayCurrent của QDateTimeEdit
    def ShowTime(self):
        self.dtDayCurrent.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dtDayCurrent.setDisplayFormat("HH:mm:ss")
    #Khởi tạo trang Parameter
    def openParameterPage(self):
        if self.page_parameter is None:  # Chỉ khởi tạo nếu chưa có
            self.page_parameter = PageParameterBackend(self, self.conn, self.page_initial)
        self.stackedWidget.setCurrentWidget(self.page_Parameter)
        self.ToggleMenu()
    #Kiểm tra trang hiện tại
    def checkParameterPage(self, index):
        """Kiểm tra nếu trang hiện tại là page_Parameter thì đảm bảo backend đã được tạo"""
        if self.stackedWidget.widget(index) == self.page_Parameter:  
            if self.page_parameter is None:  # Nếu chưa có thì tạo
                self.page_parameter = PageParameterBackend(self, self.conn, self.page_initial)
    #Khởi tạo trang Parameter_Confirm
    def checkParameterConfirmPage(self, index):
        """Kiểm tra nếu trang hiện tại là page_Parameter_Confirm thì đảm bảo backend đã được tạo"""
        if self.stackedWidget.widget(index) == self.page_Parameter_ConfimDelay:  
            if self.page_parameter_confirm is None:  # Nếu chưa có thì tạo
                self.page_parameter_confirm = PageParameterConfirmBackend(self, self.conn, self.page_initial, self.page_parameter)
    #Khởi tạo trang Dashboard
    def openDashboardPage(self):
        if self.page_dashboard is None:
            self.page_dashboard = DashboardBackend(self, self.conn, self.page_initial, self.page_parameter, self.page_parameter_confirm)
        self.stackedWidget.setCurrentWidget(self.page_Dashboard)
        self.ToggleMenu()
    #Kiểm tra trang Dashboard
    def checkDashboardPage(self, index):
        if self.stackedWidget.widget(index) == self.page_Dashboard:
            if self.page_dashboard is None:
                self.page_dashboard = DashboardBackend(self, self.conn, self.page_initial, self.page_parameter, self.page_parameter_confirm)
            if self.page_history is None:
                self.page_history = HistoryBackend(self, self.conn, self.KeyPrimary, self.page_initial)
            if self.page_admin is None:
                self.page_admin = AdminBackend(self, self.conn, self.KeyPrimary)
            if self.page_configuration is None:
                self.page_configuration = ConfigurationBackend(self, self.conn, self.KeyPrimary, self.page_parameter, self.page_initial)
    #Khởi tạo trang Configuration
    def openConfigurationPage(self):
        if self.page_configuration is None:
            self.page_configuration = ConfigurationBackend(self, self.conn, self.KeyPrimary, self.page_parameter, self.page_initial)
        self.stackedWidget.setCurrentWidget(self.page_Configuration)
        self.ToggleMenu()
    #Kiểm tra trang Configuration
    def checkConfigurationPage(self, index):
        if self.stackedWidget.widget(index) == self.page_Configuration:
            if self.page_configuration is None:
                self.page_configuration = ConfigurationBackend(self, self.conn, self.KeyPrimary, self.page_parameter, self.page_initial)
    #Khởi tạo trang History
    def openHistoryPage(self):
        if self.page_history is None:
            self.page_history = HistoryBackend(self, self.conn, self.KeyPrimary, self.page_initial)
        self.stackedWidget.setCurrentWidget(self.page_History)
        self.ToggleMenu()
    #Kiểm tra trang History
    def checkHistoryPage(self, index):
        if self.stackedWidget.widget(index) == self.page_History:
            if self.page_history is None:
                self.page_history = HistoryBackend(self, self.conn, self.KeyPrimary,self.page_initial)
    #Khởi tạo trang Admin
    def openAdminPage(self):
        if self.page_admin is None:
            self.page_admin = AdminBackend(self, self.conn, self.KeyPrimary)
        self.stackedWidget.setCurrentWidget(self.page_Admin)
        self.ToggleMenu()
    #Kiểm tra trang Admin
    def checkAdminPage(self, index):
        if self.stackedWidget.widget(index) == self.page_Admin:
            if self.page_admin is None:
                self.page_admin = AdminBackend(self, self.conn, self.KeyPrimary)
    #Tô màu cho các nút nhấn khi chuyển trang
    def updateButtonStyles(self):
        current_page = self.stackedWidget.currentWidget()
        for page, buttons in self.page_button_map.items():
            # Kiểm tra nếu trang hiện tại thuộc nhóm cần đổi màu
            is_selected = (current_page == page) or (
                page in [self.page_Parameter, self.page_Parameter_ConfimDelay]
                and current_page in [self.page_Parameter, self.page_Parameter_ConfimDelay]
            )
            for button in buttons:
                button.setProperty("selected", is_selected)
                button.style().unpolish(button)
                button.style().polish(button)
    #Phân quyền
    def apply_permissions(self):
        permission_map = {
            "1": [self.btnAdmin, self.btnAdmin1],
            "2": [self.btnDelete, self.btnModify],
            "3": [self.btnExport, self.btnExport_2],
            "4": [self.btnConfiguration, self.btnConfiguration1],
            "5": [self.btnAddData1],
        }

        for code, buttons in permission_map.items():
            for button in buttons:
                button.setEnabled(self.perm_manager.has_permission(code))

class MainWindow(QMainWindow, Ui_Login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Khởi tạo các thành phần trong UI
        self.btnShowpassword.clicked.connect(self.ShowPassword)
        #self.btnForgot.clicked.connect(self.forgot_password)
        #self.btnLogin.clicked.connect(self.login)
        self.applyShadow([self.btnLogin, self.txtPassword, self.label_2, self.txtUsername])
        #Hiển thị ProgressBar
        self.progressBar.hide()
        # Biến lưu kết nối DB
        self.conn = None
        self.KeyPrimary = None
        # Kết nối với database
        self.connectToDB()
        # Nút login
        self.btnLogin.clicked.connect(self.checkCredential)
        # Thay đổi sự kiện của trường mật khẩu
        self.txtPassword.textChanged.connect(self.handlePasswordChange)
    #Hiển thị mật khẩu
    def ShowPassword(self):
        if self.txtPassword.echoMode() == QLineEdit.EchoMode.Password:
            self.txtPassword.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.txtPassword.setEchoMode(QLineEdit.EchoMode.Password)
    #Kết nối với database
    def connectToDB(self):
        # Kết nối với database
        try:
            db_path = os.path.join(os.getcwd(), "WembleyProjectDatabase.db")
            self.conn = sqlite3.connect(db_path)
            if self.conn:
                print("Connected to database successfully")
            else:
                print("Cannot connect to database")
        except Exception as e:
            print(f"Database connection error: {e}")
    #Kiểm tra thông tin đăng nhập
    def checkCredential(self):
        self.username = self.txtUsername.text()
        self.password = self.txtPassword.text() 
        # Hiển thị ProgressBar
        self.progressBar.show()
        self.progressBar.setValue(0)
        # Cài đặt một timer để cập nhật giá trị progressBar từ 0 đến 100 trong 3 giây
        self.timer = QTimer(self)
        # Cập nhật progressBar mỗi 10ms
        self.timer.setInterval(10)  
        # Gọi hàm updateProgressBar khi timer hết thời gian
        self.timer.timeout.connect(self.updateProgressBar) 
        
        # Lấy dữ liệu từ database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Account WHERE UserName = ?", (self.username,))
        result = cursor.fetchall()
        # Kiểm tra thông tin đăng nhập
        if result:
            self.KeyPrimary = result[0][0]
            db_permissions = result[0][4]
            db_hashed_password = result[0][1]
            if bcrypt.checkpw(self.password.encode('utf-8'), db_hashed_password):
                self.perm_manager = PermissionManager(db_permissions)
                self.timer.start()
                self.statusLogin.hide()
            else:
                self.statusLogin.setText("Incorrect password")
        else:
            self.statusLogin.setText("Incorrect username")
    #Cập nhật giá trị của ProgressBar
    def updateProgressBar(self):
        # Cập nhật giá trị của progressBar từ 0 đến 100%
        current_value = self.progressBar.value()
        if current_value < 100:
            self.progressBar.setValue(current_value + 1)  # Tăng giá trị của progressBar lên 1 mỗi lần
        else:
            self.timer.stop()  # Dừng timer khi progressBar đạt 100%
            self.openMainApp()  # Mở ứng dụng chính
    #Xử lý sự kiện khi mật khẩu thay đổi
    def handlePasswordChange(self):
        # Kiểm tra xem mật khẩu có trống không
        if not self.txtPassword.text():  # Nếu mật khẩu trống
            self.statusLogin.setText("")  # Xóa thông báo lỗi nếu có
        else:
            self.statusLogin.setText("")  # Xóa thông báo lỗi khi người dùng bắt đầu nhập mật khẩu
    #Mở ứng dụng chính
    def openMainApp(self):
        # Mở ứng dụng chính và đóng cửa sổ đăng nhập
        self.mainApp = MainApp(self.conn, self.KeyPrimary, self.perm_manager)
        self.mainApp.show()
        self.close()
    #Áp dụng hiệu ứng bóng cho các đối tượng
    def applyShadow(self, objects, blur=20, x_offset=4, y_offset=4, color=QColor(0, 0, 0, 150)):
        """Áp dụng hiệu ứng bóng cho danh sách các đối tượng"""
        for obj in objects:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(blur)
            shadow.setXOffset(x_offset)
            shadow.setYOffset(y_offset)
            shadow.setColor(color)
            obj.setGraphicsEffect(shadow)

       
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    #window = MainApp()
    window.show()
    sys.exit(app.exec())
