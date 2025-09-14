###Xử lí ảnh xám###

import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import time
t1 = time.time()
in_folderpath = r"H:\APP UNIVERSITY\CODE PYTHON\DatasetRed\tr\test\bad" 
out_folderpath = r"H:\APP UNIVERSITY\CODE PYTHON\DatasetRed\tr\test\bad1"

brightness_scale = 0.55  # 50% độ sáng  
#Kiểm tra out_folderpath có tồn tại không, nếu không thì tạo mới
if not os.path.exists(out_folderpath):
    os.makedirs(out_folderpath) 

for filename in os.listdir(in_folderpath):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        img_path = os.path.join(in_folderpath, filename)
        img = cv2.imread(img_path)

        if img is not None:
            # Giảm sáng bằng cách nhân với hệ số
            darker = cv2.convertScaleAbs(img, alpha=brightness_scale, beta=0)

            out_path = os.path.join(out_folderpath, filename)
            cv2.imwrite(out_path, darker)
            print(f"Đã xử lý: {filename}")
        else:
            print(f"Không đọc được ảnh: {filename}")


