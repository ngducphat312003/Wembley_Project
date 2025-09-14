from pymelsec import Type3E
from pymelsec.constants import DT
from pymelsec.tag import Tag
import pandas as pd
import threading
import time


uri_machine_input_value = pd.read_csv(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\Document\no_rub_input_value.csv", index_col=0)
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
        
    #Ghi một giá trị BIT
    def WritePlcVariable(self, address, value1):
        if self.PLCConnection():
            try:
                with self.lock:
                    # Ghi một giá trị bit vào PLC
                    tag = Tag(device=address, value=value1, type=DT.BIT)
                    self.plc.write(devices=[tag])
                    print(f"Đã ghi giá trị {value1} vào {address}")
            except Exception as e:
                print(f"Lỗi khi ghi dữ liệu vào PLC: {e}")
    
    #Ghi một giá trị WORD
    def WritePlcVariableWord(self, address, value1):
        if self.PLCConnection():
            try:
                with self.lock:
                    # Ghi một giá trị word vào PLC
                    tag = Tag(device=address, value=value1, type=DT.UWORD)
                    self.plc.write(devices=[tag])
                    print(f"Đã ghi giá trị {value1} vào {address}")
            except Exception as e:
                print(f"Lỗi khi ghi dữ liệu vào PLC: {e}")

if __name__ == "__main__":
    plc_host = '192.168.100.14'
    plc_port = 4095
    plc_type = 'Q'
    system = ProductionSystem(plc_host, plc_port, plc_type)

    if system.PLCConnection():
        print("PLC connection is active.")
        #system.WritePlcVariable('M3', 0)
        #time.sleep(3)
        #system.WritePlcVariable("M3", 0)
        
        system.WritePlcVariableWord("D4", 950)
    else:
        print("PLC connection is inactive.")
    
    #Biến Số lượng khay: D3523 (word)
    #Biến số lượng khay tốt hiện tại: D3521 (Word)
    #Đẩy khay nếu có lỗi: M1906 (Bit)


