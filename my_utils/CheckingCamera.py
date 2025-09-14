from PyQt6.QtCore import QThread, pyqtSignal

class ConnectionCameraChecker(QThread):
    finished = pyqtSignal(bool)  # Trả về kết quả kết nối (True/False)

    def __init__(self, check_func):
        super().__init__()
        self.check_func = check_func
        self.result = False

    def run(self):
        self.result = self.check_func()  # Chạy hàm kiểm 
        # print(f"Camera connection result: {self.result}")
        self.finished.emit(self.result)  # Gửi tín hiệu khi hoàn thành