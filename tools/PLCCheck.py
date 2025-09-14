from pymelsec import Type3E
from pymelsec.constants import DT
import pandas as pd
import threading

#------------------------------------------------------------------------------------
uri_machine_input_value = pd.read_csv(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceCode\Document\no_rub_input_value.csv", index_col=0)
dinput_addr = [*uri_machine_input_value['ID_Input']]
dinput_type = [*uri_machine_input_value['Input_Type']]
dinput_name = [name.strip() for name in [*uri_machine_input_value['Input_Name']]]
dinput_index = [*uri_machine_input_value['Input_Index']]
dinput_lenght = len(dinput_addr)
dinput_old = [-1]*dinput_lenght

class ProductionSystem:
    def __init__(self, plc_host, plc_port=4095, plc_type='Q'):
        self.plc_host = plc_host
        self.plc_port = plc_port
        self.plc_type = plc_type
        self.plc = None
        self.camera = None
        self.triggered = threading.Event()  # Sự kiện kích hoạt khi lấy biến từ PLC thành công
        self.lock = threading.Lock()
        self.results = []
        self.error_logs = [] 
        self.plc_connected = False
        self.camera_connected = False
        self.image_directory = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\WhiteDatasetTask04122024"
        self.processing = False
        self.last_trigger_state = 0
        self.trigger = None  # Initialize trigger to None
        self.timestamp_S3_in_19 = None
        self.timestamp_S3_in_22 = None

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

    # 3. Lấy biến PLC để kích hoạt camera trigger
    def GetPlcVariableForTrigger(self):
        if self.PLCConnection():
            for i in range(dinput_lenght):
                try:
                    with self.lock:
                        # Đọc biến từ PLC
                        read_result = self.plc.batch_read(ref_device='X0', read_size=50, data_type=DT.BIT)
                        RealValue1 = int(read_result[29].value)

                        if dinput_old[20] != RealValue1:
                            dinput_old[20] = RealValue1
                            print("S3/in/19", RealValue1)
                                
                        trigger_value = RealValue1
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
     # Phương thức chạy hệ thống
    def Run(self):
        # Tạo và khởi động luồng cho kết nối PLC
        plc_thread = threading.Thread(target=self.PLCConnection)
        plc_thread.start()

        if self.PLCConnection():
            print("System is fully connected.")
            while True:
                self.GetPlcVariableForTrigger()
                #print("Waiting for next trigger")

                if self.triggered.is_set():
                    self.processing = True
                    print("Trigger activated, processing images...")
                    with self.lock:
                        try:
                            #time.sleep(0.3)
                            # Execute the camera trigger
                            
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
#Main
if __name__ == '__main__':
    system = ProductionSystem(plc_host='192.168.100.14')
    system.Run()

