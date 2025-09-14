import numpy as np
import cv2 
from math import *

img = cv2.imread(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\2025-04-24-09-32-52_IMG.bmp")
#Hiển thị toàn bộ ảnh
#cv2.imshow("Original Image", img)
#Chuyển ảnh màu sang ảnh xám
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
#Hiển thị ảnh xám
#cv2.imshow("Gray Image", img_gray)
img_blur = cv2.GaussianBlur(img_gray, (5,5), 0)
#Hiển thị ảnh sau khi lọc Gaussian
#cv2.imshow("Blur Image", img_blur)
# detected_circles_model1 = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, dp=1.1, minDist=80,
#                                  param1=80, param2=40, minRadius=65, maxRadius=85)
detected_circles_model1 = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, dp=1.1, minDist=90,
                                 param1=60, param2=35, minRadius=65, maxRadius=85)
pipes_count_model1 = 0

#Nắp cao su
detected_circles_model2  = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, dp=1.1, minDist=90,
                                param1=60, param2=35, minRadius=70, maxRadius=90)
pipes_count_model2 = 0



bbox_width = 125
bbox_height = 125
row_save = []
col_save = []

#Biến để thực hiện thuật toán sắp xếp vị trí các ống
pos_count = 0
x_arr = []
y_arr = []
y_search = 0
distance_tuples = []
distance_tuples1 = []
row = []
col = []

#Biến để nhận diện chấm màu đỏ
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([179, 255, 255])

#Mảng lưu các vị trí bị mất của các ống (nếu có)
rectangles_to_remove = []

def process_detected_circles(detected_circles_model):
    if detected_circles_model is not None:
        detected_circles = np.uint16(np.around(detected_circles_model))
        detected_circles = sorted(detected_circles[0, :], key=lambda x: (x[0], x[1]))
        return detected_circles
    return []

detected_circles1 = process_detected_circles(detected_circles_model1)
print(detected_circles1)
pipes_count_model1 = len(detected_circles1)

for points in detected_circles1:
        a, b, r = points[0], points[1], points[2]
        cv2.circle(img, (a, b), 1, (0, 0, 255), 3)
        
print("Total number of pipes1:", pipes_count_model1)

#Thu thập tọa độ của các ống ở cột đầu tiên
if detected_circles_model1 is not None:
    detected_circles = np.uint16(np.around(detected_circles_model1))
    for i, (x, y, _) in enumerate(detected_circles[0, :]):
        distance = sqrt((int(x))**2 + (int(y)**2))
        distance_tuples.append((distance, int(x), int(y)))
    #Lấy giá trị y nhỏ nhất của distance_tuples
    
    # distance_tuples.sort()
    while len(distance_tuples1) != 10:
        distance_tuples.sort()
        xmin = min(distance_tuples, key=lambda d: d[0])[1]
        
        # ymin = min(distance_tuples, key=lambda d: d[0])[2]
        min_y_tuple = min(distance_tuples, key=lambda x: x[2])
        min_y = min_y_tuple[2]
        max_x_tuple = max(distance_tuples, key=lambda x: x[1])
        max_x = max_x_tuple[1]
        min_x_tuple = min(distance_tuples, key=lambda x: x[1])
        min_x = min_x_tuple[1]
        print("Xmax: ", max_x)
        print("Ymin: ", min_y)
        print("Xmin: ", min_x)
        
        # Filter circles within the x-range and store them
        distance_tuples1 = [(d, x, y) for d, x, y in distance_tuples if xmin - 80 <= x <= xmin + 80]
        distance_tuples1.sort()
        if (distance_tuples1[0][2]< min_y - 50) or (distance_tuples1[0][2]> min_y + 50):
            print("Vị trí ống đầu tiên bị thiếu")
            #Lấy giá trị cột 1
            y_arr = [int(y[2]) for y in distance_tuples1]  # Lấy giá trị y từ distance_tuples1
            # Tính khoảng cách giữa các phần tử liên tiếp
            y_distances = [abs(y2 - y1) for y1, y2 in zip(y_arr, y_arr[1:])]
            x_avg = sum([x[1] for x in distance_tuples1]) / len(distance_tuples1) if distance_tuples1 else 0
            # Tính khoảng cách trung bình
            average_distance = sum(y_distances) / len(y_distances) if y_distances else 0
            print("Khoảng cách giữa các phần tử liên tiếp:", y_distances)
            print("Khoảng cách trung bình:", average_distance)
            filtered_distances = [d for d in y_distances if d <= average_distance + 70]
            new_average_distance = sum(filtered_distances) / len(filtered_distances) if filtered_distances else 0
            y_new = distance_tuples1[0][2] - new_average_distance
            distance_new = sqrt((int(x_avg))**2 + (int(y_new)**2))
            cv2.circle(img, (int(x_avg), int(y_new)), 1, (0, 100, 255), 3)
            distance_tuples.append((distance_new, int(x_avg), int(y_new)))
            distance_tuples1.append((distance_new, int(x_avg), int(y_new)))
            distance_tuples1.sort()
        else:    
            print("Vị trí ống đầu tiên không bị thiếu")
            y_arr = [int(y[2]) for y in distance_tuples1]  # Lấy giá trị y từ distance_tuples1
            # Tính khoảng cách giữa các phần tử liên tiếp
            y_distances = [abs(y2 - y1) for y1, y2 in zip(y_arr, y_arr[1:])]
            x_avg = sum([x[1] for x in distance_tuples1]) / len(distance_tuples1) if distance_tuples1 else 0
            # Tính khoảng cách trung bình
            average_distance = sum(y_distances) / len(y_distances) if y_distances else 0
            print("Khoảng cách giữa các phần tử liên tiếp:", y_distances)
            print("Khoảng cách trung bình:", average_distance)
            # Lọc ra các khoảng cách lớn hơn trung bình và lưu vị trí
            greater_than_avg = [(i, d) for i, d in enumerate(y_distances) if d > average_distance+70]
            # Tạo danh sách mới, chỉ giữ các khoảng cách không vượt quá (average_distance + 40)
            filtered_distances = [d for d in y_distances if d <= average_distance + 70]
            # Tính lại khoảng cách trung bình mới
            new_average_distance = sum(filtered_distances) / len(filtered_distances) if filtered_distances else 0
            print("Khoảng cách trung bình mới (loại bỏ outlier):", new_average_distance)
            if greater_than_avg:
                for i, d in greater_than_avg:
                    print(f"Khoảng cách lớn hơn trung bình tại vị trí {i}: {d}")
                    y_new = distance_tuples1[i][2] + new_average_distance
                    distance_new = sqrt((int(x_avg))**2 + (int(y_new)**2))
                    # cv2.circle(img, (int(x_avg), int(y_new)), 1, (0, 100, 255), 3)
                    distance_tuples.append((distance_new, int(x_avg), int(y_new)))
                    distance_tuples1.append((distance_new, int(x_avg), int(y_new)))
                    distance_tuples1.sort()
            elif len(y_distances) != 9:
                print("Tô ở vị trí thứ còn thiếu cuối cùng")
                y_last = distance_tuples1[-1][2] + new_average_distance
                # cv2.circle(img, (int(x_avg), int(y_last)), 1, (0, 100, 255), 3)
                distance_new = sqrt((int(x_avg))**2 + (int(y_last)**2))
                distance_tuples.append((distance_new, int(x_avg), int(y_last)))
                distance_tuples1.append((distance_new, int(x_avg), int(y_last)))
                distance_tuples1.sort()
    print("distance_tuples1",distance_tuples1)
    k = 0
    position = []
    while k < 10:
        count = 0 
        col_search = distance_tuples1[k][2]
        print("col_search: ",col_search)
        print("k: ",k)
        col_search_new = col_search
        while count != 10:
            for d, x, y in distance_tuples: 
                #Số 60 ở đây là khoảng cách giữa các ống           
                if (col_search_new - 100 <= y <= col_search_new + 100):
                    count +=1
                    distance_new1 = np.sqrt((int(x))**2 + (int(y))**2)
                    # print("distance_new1: ",distance_new1)
                    # cv2.circle(img, (int(x), int(y)), 3, (200, 100, 255), 3)
                    position.append((float(distance_new1), int(x), int(y)))
                    col_search_new = y
            position.sort()
            print("Count: ", count) 
            print("x_search: ",[x[1] for x in position])
            print(len(position))
            if count != 10:
                print("Vị trí: ", k+1, " không đủ 10 ống")
                y_avg1 = sum([y[2] for y in position]) / len(position) if position else 0
                x_distances1 = [abs(x2 - x1) for x1, x2 in zip([x[1] for x in position], [x[1] for x in position][1:])]
                ("Khoảng cách giữa các phần tử liên tiếp:", x_distances1)
                average_distance1 = sum(x_distances1) / len(x_distances1) if x_distances1 else 0
                print("Khoảng cách trung bình:", average_distance1)
                greater_than_avg1 = [(i, d) for i, d in enumerate(x_distances1) if d > average_distance1+80]
                print("greater_than_avg1: ", greater_than_avg1)
                # Tạo danh sách mới, chỉ giữ các khoảng cách không vượt quá (average_distance + 40)
                filtered_distance1 = [d for d in x_distances1 if d <= average_distance1 + 80]
                print("filtered_distance1: ", filtered_distance1)
                new_average_distance1 = sum(filtered_distance1) / len(filtered_distance1) if filtered_distance1 else 0
                print("Khoảng cách trung bình mới (loại bỏ outlier):", new_average_distance1)
                if len(greater_than_avg1) >= 1:
                    for i, d in greater_than_avg1:
                        print(f"Khoảng cách lớn hơn trung bình tại vị trí {i+1}: {d}")
                        x_new = position[i][1] + new_average_distance1
                        cv2.circle(img, (int(x_new), int(y_avg1)), 1, (255, 100, 255), 3)
                        distance_new2 = sqrt((int(x_new))**2 + (int(y_avg1)**2))
                        # Thêm vào danh sách và sắp xếp
                        position.append((distance_new2, int(x_new), int(y_avg1)))
                        # position.sort()
                        distance_tuples.append((distance_new2, int(x_new), int(y_avg1)))
                        print("position: ", position)

                    if len(greater_than_avg1) == 1:
                        position.clear()  # Chỉ xóa position nếu có đúng 1 phần tử
                    count = 0
                    position.clear()
                elif len(x_distances1) != 9: 
                    print("Tô ở vị trí cuối cùng")
                    x_last = position[-1][1]+average_distance1
                    cv2.circle(img, (int(x_last), int(y_avg1)), 1, (255, 100, 255), 3)
                    distance_new2 = sqrt((int(x_last))**2 + (int(y_avg1)**2))
                    position.append((distance_new2, int(x_last), int(y_avg1)))
                    distance_tuples.append((distance_new2, int(x_last), int(y_avg1)))
                    count = 0
                    position.clear()
                    position.sort()
                
        k+=1        
        # print("len of position: ", len(position))
        for distance, x, y in position:
            col.append((x))
            row.append((y))
      
        
        position.clear()
    # print("col:", col)
    # print("row:", row)
    # print("len col: ", len(col))
    # print("len row: ", len(row))
    


    #     x_arr.append(int(x))
    #     y_arr.append(int(y))

    # row.append(y_arr[0])
    # col.append(x_arr[0])
    # y_search = y_arr[0]
    # print("y_search: ",y_search)

    #Lấy trị trí từng ống của cột đầu tiên để sắp xếp vị trí các ống theo thứ tự từ nhỏ đến lớn
    # k = 0
    # while k < 10:
    #     y_search = y_arr[k]
    #     print("y_search: ",y_search)
    #     for i, (x, y, _) in enumerate(detected_circles[0, :]): 
    #         #Số 60 ở đây là khoảng cách giữa các ống           
    #         if (y_search - 100 <= y <= y_search + 100):
    #             distance1 = np.sqrt((int(x))**2 + (int(y))**2)
    #             distance_tuples1.append((int(distance1), int(x), int(y)))

    #     distance_tuples1.sort()
    #     #print("distance_tuples1",distance_tuples1)
    #     for distance, x, y in distance_tuples1:
    #         col.append(int(x))
    #         row.append(int(y))
    #     distance_tuples1.clear()
    #     k+=1
    # print(f"{col}, {row}")
    # print("len cot: ",len(col),"len hang:", len(row))
    
    # for m in range(len(col)):
    #     pos_count+=1
    #     cv2.putText(img, str(pos_count), (col[m]-18, row[m]+30), cv2.FONT_HERSHEY_PLAIN, 2, (66, 245, 233), 2, cv2.LINE_AA)
    #     top_left = (col[m] - bbox_width // 2, row[m] - bbox_height // 2)
    #     bottom_right = (col[m] + bbox_width // 2, row[m] + bbox_height // 2)
    #     cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)

#Mảng cố định vị trí các hình vuông được lấy từ col và row, với sản phẩm mới phải test qua 1 sản phẩm để lấy tọa độ
#col_save = [523, 681, 837, 1004, 1167, 1334, 1499, 1669, 1833, 2004, 524, 681, 844, 1007, 1170, 1339, 1505, 1669, 1835, 2000, 512, 679, 842, 1006, 1169, 1337, 1502, 1671, 1839, 2003, 521, 681, 842, 1005, 1170, 1336, 1502, 1673, 1839, 2000, 525, 679, 840, 1004, 1173, 1337, 1508, 1675, 1842, 2007, 529, 685, 848, 1007, 1174, 1339, 1506, 1671, 1836, 2004, 520, 683, 841, 1006, 1174, 1338, 1508, 1675, 1843, 2010, 533, 687, 848, 1011, 1173, 1338, 1505, 1671, 1842, 1998, 540, 697, 853, 1016, 1178, 1343, 1502, 1671, 1834, 1995, 535, 692, 851, 1009, 1175, 1337, 1501, 1666, 1828, 1995]
#row_save = [329, 342, 333, 340, 329, 326, 334, 322, 318, 329, 501, 500, 500, 505, 503, 504, 501, 498, 490, 490, 677, 679, 675, 669, 668, 672, 670, 672, 672, 674, 839, 848, 846, 848, 846, 846, 849, 846, 846, 842, 1024, 1020, 1020, 1015, 1017, 1014, 1022, 1019, 1021, 1019, 1189, 1185, 1187, 1193, 1187, 1185, 1190, 1194, 1189, 1198, 1365, 1352, 1354, 1359, 1360, 1363, 1359, 1359, 1358, 1369, 1530, 1526, 1534, 1537, 1538, 1526, 1527, 1530, 1537, 1530, 1693, 1697, 1699, 1699, 1706, 1693, 1690, 1697, 1697, 1698, 1851, 1855, 1858, 1856, 1863, 1873, 1874, 1868, 1874, 1867]
for m in range(len(col)):
    if m % 10 == 9 and m < 100:
        if col[m] > max_x:
            new_index = m - 9  # vị trí đầu của mỗi cột logic
            a = row[m-8]
            print("m: ", m)
            print("a: ", a)
            # Dồn các phần tử trong "cột logic" này từ new_index đến m-1 sang phải 1 vị trí
            for i in range(m - 1, new_index - 1, -1):
                col[i + 1] = col[i]
                row[i + 1] = row[i]
            # Gán giá trị mới vào đầu cột
            col[new_index] = min_x  
            row[new_index] = a
    
    
col_save = col
row_save = row
print("col: ", col_save)
print("row: ",row_save)
print("len col: ", len(col_save))
print("len row: ", len(row_save))

for m in range(len(col_save)):
    pos_count+=1
    #cv2.putText(img, str(pos_count), (col_save[m], row_save[m]), cv2.FONT_HERSHEY_PLAIN, 2, (66, 245, 233), 2, cv2.LINE_AA)
    top_left = (col_save[m] - bbox_width // 2, row_save[m] - bbox_height // 2)
    bottom_right = (col_save[m] + bbox_width // 2, row_save[m] + bbox_height // 2)
    cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)

    roi = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv_roi, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_roi, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    if not np.any(red_mask):
        # If no red circle detected, mark the rectangle for removal and notify the position
        rectangles_to_remove.append(m)
        print(f"Rectangle at position {m + 1} is being removed.")
print(pos_count)
cv2.namedWindow('Detected Circles Model 1', cv2.WINDOW_NORMAL)
cv2.imshow("Detected Circles Model 1", img)
cv2.imwrite(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembleyImage\2025-05-07-14-22-42_IMG_result.bmp", img)
cv2.waitKey(0)
cv2.destroyAllWindows()