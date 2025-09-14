import cv2
import numpy as np
frame = cv2.imread(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembleyImage\red2903\IMG_0006.bmp")
height, width, channel = frame.shape
x1 = int(width * 0.12)
x2 = int(width * 0.79)
y_start = int(height * 0.1)
y_end = int(height * 0.9)
line_color = (0, 255, 0)  # Màu xanh lá (R, G, B)
line_thickness = 2  
cv2.line(frame, (x1, y_start), (x1, y_end), line_color, line_thickness)
cv2.line(frame, (x2, y_start), (x2, y_end), line_color, line_thickness)
#Hiển thị toàn bộ hình ảnh với đường thẳng
cv2.namedWindow("Line", cv2.WINDOW_NORMAL)

cv2.imshow("Line", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
#Bar điều chỉnh threshold
# def nothing(x):
#     pass
# cv2.namedWindow("Trackbars")
# cv2.createTrackbar("Threshold", "Trackbars", 0, 255, nothing)

# while True:
#     img = cv2.imread(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult\plasticubes_IMG_0001_13.jpg")
#     threshold_value = cv2.getTrackbarPos("Threshold", "Trackbars")
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     #irode
    

#     _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

#     gray = cv2.medianBlur(gray, 5)
#     kernel = np.ones((5,5), np.uint8)
#     erode = cv2.erode(thresh, kernel, iterations=1)
#     cv2.imshow("Image", img)
#     cv2.imshow("Gray", gray)
#     cv2.imshow("Thresh", thresh)
#     cv2.imshow("Erode", erode)
#     key = cv2.waitKey(1)
#     if key == 27:
#         break

# Tạo một hình ảnh trắng với hình tròn màu đen
# img = cv2.imread(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult\plasticubes_IMG_0001_10.jpg")
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
# cv2.imshow("Image", img)
# cv2.imshow("thresh", thresh




