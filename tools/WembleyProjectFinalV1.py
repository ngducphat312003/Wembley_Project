from pymelsec import Type3E
from pymelsec.constants import DT
import threading
import os
import time
import pandas as pd
import cv2
import neoapi
from CubeDetection import run_inference, load_model
import torch
import numpy as np
#------------------------------------------------------------------------------------
uri_machine_input_value = pd.read_csv(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceCode\Document\no_rub_input_value.csv", index_col=0)
dinput_addr = [*uri_machine_input_value['ID_Input']]
dinput_type = [*uri_machine_input_value['Input_Type']]
dinput_name = [name.strip() for name in [*uri_machine_input_value['Input_Name']]]
dinput_index = [*uri_machine_input_value['Input_Index']]
dinput_lenght = len(dinput_addr)
dinput_old = [-1]*dinput_lenght

#------------------------------------------------------------------------------------ 
class ProductionSystem:
    def __init__(self, plc_host, plc_port=4095, plc_type='Q'):
        self.plc_host = plc_host
        self.plc_port = plc_port
        self.plc_type = plc_type
        self.plc = None
        self.camera = None
        self.lock = threading.Lock()
        self.triggered = threading.Event()  # Sự kiện kích hoạt khi lấy biến từ PLC thành công
        self.results = []
        self.error_logs = [] 
        self.plc_connected = False
        self.camera_connected = False
        self.image_directory = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceImages" #Nơi chứa ảnh để thực hiện object detection
        self.processing = False
        self.last_trigger_state = 0
        self.trigger = None  # Initialize trigger to None
        self.timestamp_S3_in_19 = None
        self.prediction = False

        classes_to_filter = None  # You can give list of classes to filter by name, Be happy you don't have to put class number. ['train','person']
        self.opt = {
            "weights": r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\objectdetection.pt",  # Path to weights file default weights are for nano model
            "img-size": 640,  # default image size
            "conf-thres": 0.1,  # confidence threshold for inference.
            "iou-thres": 0.45,  # NMS IoU threshold for inference.
            "device": '0' if torch.cuda.is_available() else 'cpu',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
            "classes": classes_to_filter  # list of classes to filter or None
        }
        self.model, self.device, self.half, self.stride, self.imgsz = load_model(self.opt)
        self.image_paths = [os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

    # 1. Kết nối với PLC
    def PLCConnection(self):
        if self.plc_connected:
            return True
        try:
            self.plc = Type3E(host=self.plc_host, port=self.plc_port, plc_type=self.plc_type)
            self.plc.set_access_opt(comm_type='binary')
            self.plc.connect(ip=self.plc_host, port=self.plc_port)
            print("Connecting to PLC.")
            self.plc_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to PLC: {e}")
            self.error_logs.append(str(e))
            self.plc_connected = False
            return False
    # 1.1 Kiểm tra kết nối với PLC
    def CheckPLCConnection(self):
        if self.plc_connected:
            try:
                # Đọc một biến trạng thái từ PLC để kiểm tra kết nối
                read_result = self.plc.batch_read(ref_device='X0',
                                                    read_size=50, 
                                                    data_type=DT.BIT)
                self.plc_connected = True       
                print("PLC connection is active.")    
            except Exception:
                print("PLC connection lost.")
                self.error_logs.append("PLC connection lost.")
                self.plc_connected = False  # mất kết nối
        else:
            # Nếu không có kết nối thì thử kết nối lại
            print("Attempting to reconnect to PLC...")
            self.PLCConnection()

    # 2. Kết nối camera
    def CameraConnection(self):
        # Kiểm tra xem camera đã kết nối hay chưa
        if self.camera_connected:
            return True
        try:
            self.camera = neoapi.Cam()
            self.camera.Connect()   
            if self.camera.IsConnected():
                print("Connecting to Camera.")
                self.camera_connected = True
                return True
            else:
                raise Exception("Camera not connected.")
        except (neoapi.NeoException, Exception) as e:
            print(f"Error checking camera connection: {e}")
            self.error_logs.append(str(e))
            self.camera_connected = False
            return False

    # 2.1 Kết nối camera
    def CheckCameraConnection(self):
        if self.camera_connected:
            try: 
                #self.camera = neoapi.Cam()
                ip_address = self.camera.GetFeature("GevCurrentIPAddress").GetString()
                print("Camera connection is active.")
                self.camera_connected = True
            except (neoapi.NeoException, Exception) as e:
                print(f"Error checking camera connection: {e}")
                self.error_logs.append(str(e))
                self.camera_connected = False
                
                # Nếu không có kết nối thì thử kết nối lại
                print("Attempting to reconnect to Camera...")
                self.CameraConnection()  # Gọi lại hàm để thử kết nối lại
                return False

    # 2.2 Thiết lập thông số camera   
    def ConfigCamera(self):
        if self.CameraConnection():  # Gọi kiểm tra kết nối trước khi thiết lập thông số
            try:
                # Thiết lập các thông số cho camera
                #self.camera.f.ExposureTime.Set(1000)
                self.camera.f.ExposureTime.Set(1500)
                #self.camera.f.ExposureTime.Set(1700)
                self.camera.f.Width.Set(2592)
                self.camera.f.Height.Set(2048)
                self.camera.f.OffsetX.Set(0)
                
                self.camera.f.Gain.Set(0)
                self.camera.f.PixelFormat.Set(neoapi.PixelFormat_BayerRG8)
                self.camera.SetSynchronFeatureMode(False) 
                #Tắt sharpending
                self.camera.f.TriggerMode.value = neoapi.TriggerMode_On
                self.trigger = self.camera.f.TriggerSoftware
                if self.camera.HasFeature("SharpeningEnable"):
                    self.camera.SetFeature("SharpeningEnable", False)
                if self.camera.HasFeature("NoiseReductionEnable"):
                    self.camera.SetFeature("NoiseReductionEnable", False)
                #Bật chế độ use optimal buffer size
                if self.camera.HasFeature("UseOptimalBufferSize"):
                    self.camera.SetFeature("UseOptimalBufferSize", True)
                return True
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Camera connection failed. Cannot configure settings.")
            return False

    # 3. Lấy biến PLC để kích hoạt camera trigger
    def GetPlcVariableForTrigger(self):
        if self.PLCConnection():
            for i in range(dinput_lenght):
                try:
                    with self.lock:
                        # Đọc biến từ PLC
                        read_result = self.plc.batch_read(ref_device='X0', read_size=50, data_type=DT.BIT)
                        RealValue = int(read_result[29].value)

                        if dinput_old[20] != RealValue:
                            dinput_old[20] = RealValue
                            print("S3/in/19", RealValue)
                    
                        trigger_value = RealValue
                        # Break the loop or return from the function to stop the trigger
                        if trigger_value == 1  and self.last_trigger_state == 0:  
                            self.triggered.set()  # Đặt cờ sự kiện kích hoạt
                            self.processing = True
                        elif trigger_value == 0:
                            self.processing = False  # Reset lại trạng thái xử lý khi trigger_value là 0

                        self.last_trigger_state = trigger_value  # Cập nhật trạng thái trước của trigger_value
                        return
                except Exception as e:
                    #print("Failed to get PLC variable:", e)
                    pass

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

    # Phương thức chạy hệ thống
    def Run(self):
        # Tạo và khởi động luồng cho kết nối PLC
        plc_thread = threading.Thread(target=self.PLCConnection)
        plc_thread.start()

         # Tạo và khởi động luồng cho kiểm tra camera
        camera_thread = threading.Thread(target=self.CameraConnection)
        camera_thread.start()

        # Chờ cho hai luồng kết nối PLC và camera hoàn thành
        plc_thread.join()
        camera_thread.join()

        connection_monitor_thread = threading.Thread(target=self.ConnectionMonitor)
        connection_monitor_thread.start()

        if self.PLCConnection() and self.CameraConnection():
            print("System is fully connected.")
            # Thiết lập các thông số camera sau khi kiểm tra kết nối thành công
            camera_configured = self.ConfigCamera()
            if not camera_configured:
                print("Camera configuration failed.")
                return  # Thoát nếu cấu hình camera không thành công
            while True:
                self.GetPlcVariableForTrigger()
                print("Waiting for next trigger")
                #self.image_paths = [os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

                if self.triggered.is_set():
                    self.processing = True
                    print("Trigger activated, processing images...")
                    with self.lock:
                        try:
                            time.sleep(1.195)
                            # Execute the camera trigger
                            if self.trigger:
                                self.trigger.Execute()
                            else:
                                print("Trigger is not initialized.")
                            time.sleep(0.05) 
                            img_camera = self.camera.GetImage()
                            file_path = self.GetNextFilename()
                            img_camera.Save(file_path)
                            print(f"Image saved at {file_path}")
                            self.image_paths = [os.path.join(self.image_directory, f) for f in os.listdir(self.image_directory) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
                            if self.image_paths:
                                print("There are images in the image_paths list.")
                                for image_path in self.image_paths:
                                    results = run_inference(self.model, self.device, self.half, self.stride, self.imgsz, image_path, self.opt)
                                    for class_name, confidence, cropped_img in results:
                                        print(f"Class: {class_name}, Confidence: {confidence:.2f}")
                                        if class_name == 'foamtrays' and confidence > 0.6:
                                            self.prediction = True
                                    if self.prediction:
                                        #Tạo và khởi động hai luồng song song cho task 1 và task 2
                                        task1_thread = threading.Thread(target=self.Task1, args=(cropped_img,))
                                        task2_thread = threading.Thread(target=self.Task2, args=(cropped_img,))

                                        task1_thread.start()
                                        task2_thread.start()

                                        #Kiểm tra kết quả khi các luồng hoàn thành
                                        while task1_thread.is_alive() or task2_thread.is_alive():
                                            time.sleep(0.1)  # Tạm dừng một chút trước khi kiểm tra lại
                                        # Reset biến dự đoán
                                        self.prediction = False
                                        
                                        # Reset trigger sau khi hoàn thành xử lý
                                #Xóa ảnh đã có ở trong thư mục image_paths
                                os.remove(image_path)
                            else:
                                print("No images in the image_paths list.")
                            self.triggered.clear()  # Đặt lại trigger để chờ lần kích hoạt tiếp theo
                            self.processing = False  
                        except Exception as e:
                            print(f"Error capturing or saving image: {e}")
                        finally:
                            # Reset trigger sau khi hoàn thành xử lý
                            self.triggered.clear()
                            self.processing = False
                # else:
                #     time.sleep(0.01)
                    
        else:
            print("System setup failed.")

    # 4. Task1: Counting
    def Task1(self, img):
        self.triggered.wait()  # Chờ cho đến khi trigger được kích hoạt
        print("Starting task 1 preprocessing...")
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #Làm mịn ảnh   
        img_blur = cv2.GaussianBlur(img_gray, (5,5), 0)
        #Nắp cao su
        # circles = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, dp=1.1, minDist=80,
        #                                param1=60, param2=35, minRadius=70, maxRadius=90)
        #Nắp nhựa
        circles = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, dp=1.1, minDist=80,
                                        param1=80, param2=40, minRadius=65, maxRadius=85)
        #Nắp nhựa trắng
        # circles = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, dp=1.25, minDist=100,
        #                                 param1=80, param2=40, minRadius=68, maxRadius=80)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            num_circles = len(circles)
            print(f"Số lượng hình tròn được phát hiện: {num_circles}")
        else:
            print("Không tìm thấy hình tròn nào.")

        for (x, y, r) in circles:
            # Vẽ hình tròn lên ảnh gốc
            cv2.circle(img, (x, y), r, (0, 255, 0), 4)
            # Vẽ tâm của hình tròn
            cv2.circle(img, (x, y), 2, (0, 128, 255), 3)
        cv2.imwrite("HoughCircles7.jpg", img)
        print("Task 1 preprocessing complete.")
        return num_circles
    
    # 5. Task2: Infect detection
    def Task2(self, image):
        self.triggered.wait()  # Chờ cho đến khi trigger được kích hoạt
        print("Starting task 2 preprocessing...")

        print("Task 2 preprocessing complete.")
        return
    

    def ConnectionMonitor(self):
        # Luồng kiểm tra kết nối định kỳ.
        while True:
            # Kiểm tra kết nối PLC
            self.CheckPLCConnection()
            if not self.plc_connected:
                print("PLC connection lost. Attempting to reconnect...")
                self.PLCConnection()
            self.CheckCameraConnection()
            # Kiểm tra kết nối camera
            if not self.camera_connected:
                print("Camera connection lost. Attempting to reconnect...")
                self.CameraConnection()
            
            time.sleep(5)  # Đợi 5 giây trước khi kiểm tra lại

#Main
if __name__ == '__main__':
    system = ProductionSystem(plc_host='192.168.100.14')
    system.Run()
