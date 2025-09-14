import cv2
import os

# # Đường dẫn ảnh gốc và thư mục đích
# img_path = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\AnomalyGreyDataset\BlackBGCube\ground_truth\segmentation"
# img_dest = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\AnomalyGreyDataset\BlackBGCube\ground_truth\segmentation1"

# # Đọc các ảnh từ thư mục img_path
# for file_name in os.listdir(img_path):
#     # Kiểm tra nếu file là ảnh
#     if file_name.endswith('.jpg') or file_name.endswith('.png'):  # Có thể thêm các định dạng ảnh khác nếu cần
       
#         # Đọc ảnh
#         img = cv2.imread(os.path.join(img_path, file_name))
#         print(os.path.splitext(file_name)[0])
#         # Xử lý ảnh, ví dụ: chuyển sang ảnh đen trắng (thresh là ảnh đã được xử lý)
#         # Giả sử ở đây bạn thực hiện một xử lý nào đó, ví dụ như thresholding
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
#         cv2.imshow('thresh', thresh)
#         # Lưu ảnh với định dạng .bmp
#         file_name_bmp = os.path.splitext(file_name)[0] + '.bmp'  # Đổi phần mở rộng thành .bmp
#         cv2.imwrite(os.path.join(img_dest, file_name_bmp), thresh)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# img = cv2.imread(r"H:\APP UNIVERSITY\CODE PYTHON\frame.jpg")
# #Hiển thị thông tin màu
# cv2.imshow('image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

import cv2

# Đọc ảnh
img = cv2.imread(r"H:\APP UNIVERSITY\CODE PYTHON\frame.jpg")
clone = img.copy()  # Tạo bản sao để vẽ

# Biến lưu trạng thái vẽ
drawing = False  # Đang vẽ hay không
start_x, start_y = -1, -1  # Tọa độ bắt đầu
rectangles = []  # Danh sách hình chữ nhật

# Hàm xử lý sự kiện chuột
def draw_rectangle(event, x, y, flags, param):
    global start_x, start_y, drawing, img, clone

    if event == cv2.EVENT_LBUTTONDOWN:  # Khi nhấn chuột trái
        drawing = True
        start_x, start_y = x, y

    elif event == cv2.EVENT_MOUSEMOVE:  # Khi di chuyển chuột
        if drawing:
            img = clone.copy()  # Reset ảnh
            cv2.rectangle(img, (start_x, start_y), (x, y), (0, 255, 0), 2)
            # Hiển thị tọa độ tạm thời khi vẽ
            text = f"({start_x}, {start_y}) -> ({x}, {y})"
            cv2.putText(img, text, (start_x, start_y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    elif event == cv2.EVENT_LBUTTONUP:  # Khi nhả chuột
        drawing = False
        width = abs(x - start_x)
        height = abs(y - start_y)

        # Lưu thông số
        rectangles.append((start_x, start_y, width, height))

        # Vẽ hình chữ nhật cố định
        cv2.rectangle(img, (start_x, start_y), (x, y), (0, 255, 0), 2)

        # Hiển thị thông số trên ảnh
        text = f"x={start_x}, y={start_y}, w={width}, h={height}"
        cv2.putText(img, text, (start_x, start_y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

# Tạo cửa sổ và gán sự kiện chuột
cv2.namedWindow("Draw Rectangles", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Draw Rectangles", draw_rectangle)

while True:
    cv2.imshow("Draw Rectangles", img)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("q"):  # Nhấn 'q' để thoát
        break

# In danh sách hình chữ nhật đã vẽ
print("Danh sách hình chữ nhật (x, y, width, height):")
for rect in rectangles:
    print(rect)

cv2.destroyAllWindows()
