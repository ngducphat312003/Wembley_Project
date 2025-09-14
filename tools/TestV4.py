import time
import cv2
import torch
import numpy as np
import os
from numpy import random
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords, set_logging
from utils.plots import plot_one_box
from utils.torch_utils import select_device
from pathlib import Path
import os, shutil
# from torchvision.transforms import transforms
from collections import Counter
# from torchvision.models import mobilenet_v3_large
from torchvision.transforms import transforms
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights
from PIL import Image
import onnxruntime as ort

# from tqdm.auto import tqdm
# import matplotlib.pyplot as plt
# import seaborn as sns
#Train
#34, 36, 38, 40, 32
#Test
#1006, 1003
#TestModel
#


# def letterbox(img, new_shape=(576, 576), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
#     shape = img.shape[:2]  # current shape [height, width]
#     if isinstance(new_shape, int):
#         new_shape = (new_shape, new_shape)

#     r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
#     if not scaleup:  # only scale down, do not scale up (for better test mAP)
#         r = min(r, 1.0)

#     ratio = r, r  # width, height ratios
#     new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
#     dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
#     if auto:  # minimum rectangle
#         dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
#     elif scaleFill:  # stretch
#         dw, dh = 0.0, 0.0
#         new_unpad = (new_shape[1], new_shape[0])
#         ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

#     dw /= 2  # divide padding into 2 sides
#     dh /= 2

#     if shape[::-1] != new_unpad:  # resize
#         img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
#     top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
#     left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
#     img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
#     return img, ratio, (dw, dh)

def letterbox(img, new_shape=(576, 576), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)



# Tải mô hình một lần và giữ nó trong bộ nhớ
# def load_model(opt):
#     # set_logging()
#     # device = select_device(opt['device'])
#     # half = device.type != 'cpu'
#     # model = attempt_load(opt['weights'], map_location=device)  # load FP32 model
#     # stride = int(model.stride.max())  # model stride
#     # imgsz = check_img_size(opt['img-size'], s=stride)  # check img_size
#     # if half:
#     #     model.half()
#     # print(f"Using device: {device}")  # Thêm thông báo để xác nhận thiết bị đang sử dụng
#     set_logging()
#     device = select_device(opt['device'])
#     half = device.type != 'cpu'

#     weights = opt['weights']
#     if weights.endswith('.torchscript.pt'):
#         # Load TorchScript model
#         model = torch.jit.load(weights, map_location=device)
#         model.eval()
#         if half:
#             model.half()
#         # Không có stride trong TorchScript, set mặc định
#         stride = 64  # hoặc 64 tùy YOLOv7 bạn export từ đâu
#         model.names = ['blplastic', 'brplastic', 'foamtrays', 'midplastic', 'nonplastic', 'plastictrays','rubbertrays','tlplastic','trplastic']
#     else:
#         # Load PyTorch .pt model thông thường
#         model = attempt_load(weights, map_location=device)  # load FP32 model
#         stride = int(model.stride.max())
#         if half:
#             model.half()

#     imgsz = check_img_size(opt['img-size'], s=stride)
#     print(f"✅ Loaded model from: {weights}")
#     print(f"📌 Using device: {device}, FP16: {half}")
#     return model, device, half, stride, imgsz

def load_model(opt):
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if opt['device'] != 'cpu' else ['CPUExecutionProvider']
    session = ort.InferenceSession(opt['weights'], providers=providers)

    input_name = session.get_inputs()[0].name
    output_names = [output.name for output in session.get_outputs()]

    print(f"✅ Loaded ONNX model from: {opt['weights']}")
    print(f"📌 Providers: {session.get_providers()}")
    print(f"📐 ONNX expected input shape: {session.get_inputs()[0].shape}")

    names = ['blplastic', 'brplastic', 'foamtrays', 'midplastic', 'nonplastic', 'plastictrays',
             'rubbertrays', 'tlplastic', 'trplastic']

    # Use shape from ONNX input for imgsz
    onnx_input_shape = session.get_inputs()[0].shape
    try:
        imgsz = int(onnx_input_shape[2])  # ví dụ: 640
    except (TypeError, ValueError):
        imgsz = int(opt['img-size'])  # fallback nếu shape là 'height' (string)

    stride = 32  # usually 32 for YOLO

    return session, input_name, output_names, stride, imgsz, names
# Hàm để thực hiện suy luận
# def run_inference(model, device, half, stride, imgsz, source_image_path, opt):
#     img0 = cv2.imread(source_image_path)
#     img = letterbox(img0, imgsz, stride=stride)[0]
#     img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
#     img = np.ascontiguousarray(img)
#     img = torch.from_numpy(img).to(device)
#     img = img.half() if half else img.float()  # uint8 to fp16/32
#     img /= 255.0  # 0 - 255 to 0.0 - 1.0
#     if img.ndimension() == 3:
#         img = img.unsqueeze(0)

#     # Get class names
#     names = model.module.names if hasattr(model, 'module') else model.names

#     # Generate colors for each class
#     colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

#     # Inference
#     with torch.no_grad():  # Disable gradient calculation for inference
#         # pred = model(img, augment=False)[0]
#         pred = model(img)[0]

#     # Apply NMS
#     classes = None
#     if opt['classes']:
#         classes = []
#         for class_name in opt['classes']:
#             classes.append(opt['classes'].index(class_name))

#     pred = non_max_suppression(pred, opt['conf-thres'], opt['iou-thres'], classes=classes, agnostic=False)
#     results = []
#     output_dir2 = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult"
#     for i, det in enumerate(pred):
#         s = ''
#         s += '%gx%g ' % img.shape[2:]  # print string
#         #gn = torch.tensor(img0.shape)[[1, 0, 1, 0]]
#         if len(det):
#             det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()

#             for c in det[:, -1].unique():
#                 n = (det[:, -1] == c).sum()  # detections per class
#                 s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

#             for j, (*xyxy, conf, cls) in enumerate(reversed(det)):
#                 # label = f'{names[int(cls)]} {conf:.2f}'
#                 # plot_one_box(xyxy, img0, label=label, color=colors[int(cls)], line_thickness=3)
#                 # if names[int(cls)] == "foamtrays" :  # Chỉ xử lý class 'plasticubes'
#                 if names[int(cls)] == 'midplastic' and conf.item() <= 0.8:
#                     continue
#                 elif names[int(cls)] == 'foamtrays':
#                     continue
#                 elif names[int(cls)] == 'brplastic' and conf.item() <= 0.7:
#                     continue
#                 elif names[int(cls)] == 'blplastic' and conf.item() <= 0.7:
#                     continue
#                 elif names[int(cls)] == 'tlplastic' and conf.item() <= 0.7:
#                     continue
#                 elif names[int(cls)] == 'trplastic' and conf.item() <= 0.7:
#                     continue
                
                
#                 # Append class name, confidence score, and cropped image to results
#                 xyxy = [int(x) for x in xyxy]
#                 # cropped_img = img0[xyxy[1]-10:xyxy[3]+10, xyxy[0]-10:xyxy[2]+10]
#                 cropped_img = img0[xyxy[1]:xyxy[3], xyxy[0]:xyxy[2]]
#                 gray_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
#                 gray_3channel = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

                
#                 cv2.imwrite(
#                     os.path.join(
#                         output_dir2,
#                         f'{names[int(cls)]}_{os.path.basename(source_image_path).split(".")[0]}_{j}.bmp'
#                     ),
#                     gray_3channel
#                 )
#                 #Lưu thêm tên file gốc vào kết quả
#                 results.append((names[int(cls)], conf.item(), f'{names[int(cls)]}_{os.path.basename(source_image_path).split(".")[0]}_{j}.bmp', xyxy))
                    
#     return results

def run_inference(session, input_name, output_names, stride, imgsz, source_image_path, opt, class_names):
    img0 = cv2.imread(source_image_path)

    img, ratio, (dw, dh) = letterbox(
        img0,
        new_shape=(imgsz, imgsz),
        auto=False,
        scaleFill=True,   # bắt buộc stretch cứng để đúng shape
        scaleup=True,
        stride=stride
    )

    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, HWC to CHW
    img = np.ascontiguousarray(img, dtype=np.float32) / 255.0
    img = np.expand_dims(img, axis=0)  # (1, 3, H, W)

    assert img.shape == (1, 3, imgsz, imgsz), f"❌ Image shape mismatch: {img.shape} != (1, 3, {imgsz}, {imgsz})"

    outputs = session.run(output_names, {input_name: img})  # ONNX inference

    pred = outputs[0]
    pred = torch.tensor(pred)

    pred = non_max_suppression(pred, opt['conf-thres'], opt['iou-thres'], agnostic=False)

    output_dir2 = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult"
    os.makedirs(output_dir2, exist_ok=True)

    results = []
    for i, det in enumerate(pred):
        if len(det):
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()
            for j, (*xyxy, conf, cls) in enumerate(reversed(det)):
                class_name = class_names[int(cls)]
                if (class_name == 'midplastic' and conf.item() <= 0.8) or \
                   (class_name == 'foamtrays') or \
                   (class_name in ['brplastic', 'blplastic', 'tlplastic', 'trplastic'] and conf.item() <= 0.7):
                    continue

                xyxy = [int(x) for x in xyxy]
                cropped_img = img0[xyxy[1]:xyxy[3], xyxy[0]:xyxy[2]]
                gray_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
                gray_3channel = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

                save_path = os.path.join(output_dir2, f'{class_name}_{Path(source_image_path).stem}_{j}.bmp')
                cv2.imwrite(save_path, gray_3channel)

                results.append((class_name, conf.item(), os.path.basename(save_path), xyxy))

    return results

def setup_ad():
    transform = transforms.Compose([ transforms.Resize((224,224)), transforms.ToTensor() ])
    
    # class efficientnet_feature_extractor(torch.nn.Module):
    #     def __init__(self):
    #         """This class extracts the feature maps from a pretrained EfficientNetV2-M model."""
    #         super(efficientnet_feature_extractor, self).__init__()
    #         # Tải mô hình EfficientNetV2-M với trọng số đã huấn luyện
    #         self.model = efficientnet_v2_m(weights=EfficientNet_V2_M_Weights.DEFAULT)

    #         # Đặt chế độ đánh giá và tắt gradient
    #         self.model.eval()
    #         for param in self.model.parameters():
    #             param.requires_grad = False

    #         # Hook để trích xuất feature maps
    #         def hook(module, input, output):
    #             """Lưu lại các feature maps từ các tầng cụ thể."""
    #             self.features.append(output)

    #         self.model.features[3].register_forward_hook(hook)
    #         self.model.features[4].register_forward_hook(hook)  # Tầng giữa (middle layer)
    #         self.model.features[6].register_forward_hook(hook)  # Tầng sâu hơn (deeper layer)

    #     def forward(self, input):
    #         """Truyền đầu vào qua mô hình và thu thập feature maps."""
    #         self.features = []  # Để lưu các feature maps
    #         with torch.no_grad():
    #             _ = self.model(input)  # Truyền qua mô hình

    #         # Feature maps từ các hook
    #         resized_maps = [
    #             torch.nn.functional.adaptive_avg_pool2d(fmap, (28, 28)) for fmap in self.features
    #         ]
    #         patch = torch.cat(resized_maps, 1)  # Nối các feature maps
    #         patch = patch.reshape(patch.shape[1], -1).T  # Chuyển thành tensor dạng cột

    #         return patch
    class mobilenet_feature_extractor(torch.nn.Module):
        def __init__(self):
            super(mobilenet_feature_extractor, self).__init__()
        # Tải mô hình MobileNetV3 với trọng số đã huấn luyện
            self.model = mobilenet_v3_large(weights=MobileNet_V3_Large_Weights.DEFAULT)

            # Đặt chế độ đánh giá và tắt gradient
            self.model.eval()
            for param in self.model.parameters():
                param.requires_grad = False

            # Hook để trích xuất feature maps
            self.features = []
            def hook(module, input, output):
                """Lưu lại các feature maps từ các tầng cụ thể."""
                self.features.append(output)

            # Đăng ký hook vào các tầng mà bạn muốn trích xuất feature maps
            self.model.features[3].register_forward_hook(hook)  # Tầng giữa (middle layer)
            self.model.features[6].register_forward_hook(hook)  # Tầng sâu hơn (deeper layer)
            self.model.features[12].register_forward_hook(hook) # Một tầng sâu hơn nữa (deep layer)

        def forward(self, input):
            """Truyền đầu vào qua mô hình và thu thập feature maps."""
            self.features = []  # Để lưu các feature maps
            with torch.no_grad():
                _ = self.model(input)  # Truyền qua mô hình

            # Feature maps từ các hook
            resized_maps = [
                torch.nn.functional.adaptive_avg_pool2d(fmap, (28, 28)) for fmap in self.features
            ]
            patch = torch.cat(resized_maps, 1)  # Nối các feature maps
            patch = patch.reshape(patch.shape[1], -1).T  # Chuyển thành tensor dạng cột

            return patch
        # Backbone = resnet_feature_extractor().cuda()

    #backbone = efficientnet_feature_extractor().cuda()
    backbone = mobilenet_feature_extractor().cuda()
    memory_bankbl = torch.load(r"H:\HK242\LVTN\Model\BLACKPLASTIC\memory_bank_black_bl_v2.pt", weights_only=True).cuda()
    memory_bankbr = torch.load(r"H:\HK242\LVTN\Model\BLACKPLASTIC\memory_bank_black_br_v2.pt",  weights_only=True).cuda()
    memory_bankmid = torch.load(r"H:\HK242\LVTN\Model\BLACKPLASTIC\memory_bank_black_mid_v2.pt",  weights_only=True).cuda()
    memory_banktl = torch.load(r"H:\HK242\LVTN\Model\BLACKPLASTIC\memory_bank_black_tl_v2.pt",  weights_only=True).cuda()
    memory_banktr = torch.load(r"H:\HK242\LVTN\Model\BLACKPLASTIC\memory_bank_black_tr_v2.pt",  weights_only=True).cuda()
    return backbone, memory_banktl, memory_banktr, memory_bankmid, memory_bankbl, memory_bankbr, transform
    # return backbone, transform

if __name__ == '__main__':
    # Thiết lập các tham số và đường dẫn
    classes_to_filter = None  # You can give list of classes to filter by name, Be happy you don't have to put class number. ['train','person']
    source_folder_path = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\SourceImages"
    opt = {
        "weights": r"H:\HK242\LVTN\Model\yolov7x.onnx",  # Path to weights file default weights are for nano model
        "img-size": 576,  # default image size
        "conf-thres": 0.5,  # confidence threshold for inference.
        "iou-thres": 0.45,  # NMS IoU threshold for inference.
        "device": '0' if torch.cuda.is_available() else 'cpu',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
        "classes": classes_to_filter  # list of classes to filter or None
    }
    t1 = time.time()
    # Tải mô hình một lần
    # model, device, half, stride, imgsz = load_model(opt)
    session, input_name, output_names, stride, imgsz, names = load_model(opt)
    backbone, memory_banktl, memory_banktr, memory_bankmid, memory_bankbl, memory_bankbr, transform =  setup_ad()
    # backbone, memory_bankbl, memory_bankbr, memory_bankmid, memory_banktl, memory_banktr, transform =  setup_ad()
    # backbone, transform = setup_ad()
  
    t2 = time.time()
    print(f'Load Done. ({t2 - t1:.3f}s)')
    # Lấy danh sách các ảnh trong thư mục
    image_paths = [os.path.join(source_folder_path, f) for f in os.listdir(source_folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    t3 = time.time()
    # # Thực hiện suy luận cho từng ảnh trong thư mục
    class_counter = Counter()

    for image_path in image_paths:
        # results = run_inference(model, device, half, stride, imgsz, image_path, opt)
        results = run_inference(
        session=session,
        input_name=input_name,
        output_names=output_names,
        stride=stride,
        imgsz=imgsz,
        source_image_path=image_path,
        opt=opt,
        class_names=names
        )
        # os.remove(image_path)
        print("length of results: ", len(results))
        if len(results) < 100:
            print("Ten file: ", os.path.basename(image_path))
        for class_name, confidence, file, pos in results:
            class_counter[class_name] += 1
            print(f"Class: {class_name}, Confidence: {confidence:.2f}")
            print(f"Image: {file}")
        print("Predicted class counts:")
        for cls, count in class_counter.items():
            print(f"- {cls}: {count} times")

    t4 = time.time()
    print(f'Model. ({t4 - t3:.3f}s)')
    print(f'Check. ({t4 - t2:.3f}s)')
    print(f'Done. ({t4 - t1:.3f}s)')
    # input_folder = r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult"
    
    # # Đảm bảo backbone ở chế độ đánh giá
    # backbone.eval()
    # # Đường dẫn đến thư mục cần kiểm tra
    # test_path = Path(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult")
    # results_counter = Counter()

    # plastic_config = {
    # "blplastic_": (memory_bankbl, 11.01125907897949),
    # "brplastic_": (memory_bankbr, 10.78709888458252),
    # "midplastic_": (memory_bankmid, 10.86799335479736),
    # "tlplastic_": (memory_banktl, 10.76762676239014),
    # "trplastic_": (memory_banktr, 11.50381565093994),
    # }


    # # # Lặp qua tất cả các tệp .jpg trong thư mục
    # for path in test_path.glob('*.bmp'):
    #     t6 = time.time()
    #     file_path = str(path)
    #     img = cv2.imread(file_path)
    #     h, w = img.shape[:2]

    #     # ===== Tô trắng bốn góc ảnh =====
    #     triangles = [
    #         ([int(h / 3.25), 0], [0, 0], [0, int(w / 3.25)]),  # Trên trái
    #         ([0, int(2 * h / 2.75)], [0, h], [int(w / 3.25), h]),  # Dưới trái
    #         ([w, int(h / 3)], [w, 0], [int(2 * w / 2.75), 0]),  # Trên phải
    #         ([int(2 * w / 2.75), h], [w, h], [w, int(2 * h / 2.75)])  # Dưới phải
    #     ]
    #     for pts in triangles:
    #         cv2.fillPoly(img, [np.array(pts, np.int32).reshape((-1, 1, 2))], (255, 255, 255))

    #     # Chuyển từ BGR sang RGB, sau đó sang PIL để biến đổi
    #     pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    #     test_image = transform(pil_image).cuda().unsqueeze(0)

    #     # Xác định loại plastic và thực hiện dự đoán
    #     for plastic, (memory_bank, threshold) in plastic_config.items():
    #         if plastic in path.name:
    #             with torch.no_grad():
    #                 features = backbone(test_image)
    #                 distances = torch.cdist(features, memory_bank, p=2.0)
    #                 s_star = torch.max(torch.min(distances, dim=1).values)
    #                 y_score_image = s_star.cpu().numpy()
    #                 y_pred_image = 1 * (y_score_image >= threshold)
    #                 class_label = ['GOOD', 'BAD']
    #                 results_counter[class_label[y_pred_image]] += 1
    #                 t7 = time.time()
    #                 print("time once processing: ", t7 - t6)
    #                 print(f'File name: {path.name}')
    #                 print(f'Detective score: {y_score_image:0.9f}')
    #                 print(f'Prediction: {class_label[y_pred_image]}')
    #             break  # Thoát vòng lặp khi đã xác định được loại plastic


    # t8 = time.time()
    # print(f'Processing Finished. ({t8 - t2:.3f}s)')
    # print(f"GOOD: {results_counter['GOOD']}")
    # print(f"BAD: {results_counter['BAD']}")

    # Lặp qua tất cả các tệp .bmp trong thư mục
    # for path in test_path.glob('*.jpg'):  # Tìm các tệp .bmp trong thư mục 'bad'
    #     t6 = time.time()
    #     file_path = str(path)
    #     img = cv2.imread(file_path)
    #     # if img is None:
    #     #     print(f"Không thể đọc ảnh: {file_path}")
    #     #     continue
    #     h, w = img.shape[:2]
    #     # ===== Tam giác góc trên bên trái =====
    #     x1 = [int(h / 3.25), 0]
    #     y1 = [0, int(w / 3.25)]
    #     a1 = [0, 0] 
    #     pts = np.array([x1, a1, y1], np.int32).reshape((-1, 1, 2))
    #     cv2.fillPoly(img, [pts], (255, 255, 255))
    #     # ===== Tam giác góc dưới bên trái =====
    #     x2 = [0, int(2 * h / 2.75)]
    #     y2 = [int(w / 3.25), h]
    #     a2 = [0, h]
    #     pts1 = np.array([x2, a2, y2], np.int32).reshape((-1, 1, 2))
    #     cv2.fillPoly(img, [pts1], (255, 255, 255))
    #     # ===== Tam giác góc trên bên phải =====
    #     x3 = [w, int(h / 3)]  # Điểm cạnh phải, lệch xuống
    #     y3 = [int(2 * w / 2.75), 0]  # Điểm cạnh trên, lệch sang trái
    #     a3 = [w, 0]  # Góc trên bên phải
    #     pts2 = np.array([x3, a3, y3], np.int32).reshape((-1, 1, 2))
    #     cv2.fillPoly(img, [pts2], (255, 255, 255))
    #     # ===== Tam giác góc dưới bên phải =====
    #     x4 = [int(2 * w / 2.75), h]  # Điểm cạnh dưới, lệch sang trái
    #     y4 = [w, int(2 * h / 2.75)]  # Điểm cạnh phải, lệch lên
    #     a4 = [w, h]  # Góc dưới bên phải
    #     pts3 = np.array([x4, a4, y4], np.int32).reshape((-1, 1, 2))
    #     cv2.fillPoly(img, [pts3], (255, 255, 255))
    #     # Chuyển từ BGR sang RGB (vì OpenCV đọc ảnh theo BGR, còn PIL cần RGB)
    #     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     # cv2.imshow('Result', img_rgb)
    #     # cv2.waitKey(0)
    #     # cv2.destroyAllWindows()
    #     # Chuyển ảnh OpenCV thành PIL để dùng với transform
    #     pil_image = Image.fromarray(img_rgb)
    #     if "blplastic_" in path.name:  
    #         test_image1 = transform(pil_image).cuda().unsqueeze(0)
    #         # Dự đoán với mô hình
    #         with torch.no_grad():
    #             features1 = backbone(test_image1)
    #         # Tính toán khoảng cách
    #         distances1 = torch.cdist(features1, memory_bankbl, p=2.0)
    #         dist_score1, dist_score_idxs1 = torch.min(distances1, dim=1)
    #         s_star1 = torch.max(dist_score1)
    #         # Tính điểm bất thường
    #         y_score_image1 = s_star1.cpu().numpy()
    #         y_pred_image1 = 1 * (y_score_image1 >= 12.854572296)
    #         class_label = ['GOOD', 'BAD']
    #         results_counter[class_label[y_pred_image1]] += 1
    #         # In kết quả
    #         # print(f'File name: {path.name}')
    #         # print(f'Detective score: {y_score_image1:0.9f}')
    #         # print(f'Prediction: {class_label[y_pred_image1]}')
    #         # t7 = time.time()
    #         # print(f'Once Processing. ({t7 - t6:.3f}s)')
    #     elif "brplastic_" in path.name:
    #         test_image2 = transform(pil_image).cuda().unsqueeze(0)
    #         # Dự đoán với mô hình
    #         with torch.no_grad():
    #             features2 = backbone(test_image2)
    #         # Tính toán khoảng cách
    #         distances2 = torch.cdist(features2, memory_bankbr, p=2.0)
    #         dist_score2, dist_score_idxs2 = torch.min(distances2, dim=1)
    #         s_star2 = torch.max(dist_score2)
    #         # Tính điểm bất thường
    #         y_score_image2 = s_star2.cpu().numpy()
    #         y_pred_image2 = 1 * (y_score_image2 >= 12.45312771)
    #         class_label = ['GOOD', 'BAD']
    #         results_counter[class_label[y_pred_image2]] += 1
    #         # In kết quả
    #         # print(f'File name: {path.name}')
    #         # print(f'Detective score: {y_score_image2:0.9f}')
    #         # print(f'Prediction: {class_label[y_pred_image2]}')
    #         # t7 = time.time()
    #         # print(f'Once Processing. ({t7 - t6:.3f}s)')
    #     elif "midplastic_" in path.name:
    #         test_image3 = transform(pil_image).cuda().unsqueeze(0)
    #         # Dự đoán với mô hình
    #         with torch.no_grad():
    #             features3 = backbone(test_image3)
    #         # Tính toán khoảng cách
    #         distances3 = torch.cdist(features3, memory_bankmid, p=2.0)
    #         dist_score3, dist_score_idxs3 = torch.min(distances3, dim=1)
    #         s_star3 = torch.max(dist_score3)
    #         # Tính điểm bất thường
    #         y_score_image3 = s_star3.cpu().numpy()
    #         y_pred_image3 = 1 * (y_score_image3 >= 13.345383644104004)
    #         class_label = ['GOOD', 'BAD']
    #         results_counter[class_label[y_pred_image3]] += 1
    #         # In kết quả
    #         # print(f'File name: {path.name}')
    #         # print(f'Detective score: {y_score_image3:0.9f}')
    #         # print(f'Prediction: {class_label[y_pred_image3]}')
    #         # t7 = time.time()
    #         # print(f'Once Processing. ({t7 - t6:.3f}s)')
    #     elif "tlplastic_" in path.name:
    #         test_image4 = transform(pil_image).cuda().unsqueeze(0)
    #         # Dự đoán với mô hình
    #         with torch.no_grad():
    #             features4 = backbone(test_image4)
    #         # Tính toán khoảng cách
    #         distances4 = torch.cdist(features4, memory_banktl, p=2.0)
    #         dist_score4, dist_score_idxs4 = torch.min(distances4, dim=1)
    #         s_star4 = torch.max(dist_score4)
    #         # Tính điểm bất thường
    #         y_score_image4 = s_star4.cpu().numpy()
    #         y_pred_image4 = 1 * (y_score_image4 >= 12.23159122467041)
    #         class_label = ['GOOD', 'BAD']
    #         results_counter[class_label[y_pred_image4]] += 1
    #         # In kết quả
    #         # print(f'File name: {path.name}')
    #         # print(f'Detective score: {y_score_image4:0.9f}')
    #         # print(f'Prediction: {class_label[y_pred_image4]}')
    #         # t7 = time.time()
    #         # print(f'Once Processing. ({t7 - t6:.3f}s)')
    #     elif "trplastic_" in path.name:
    #         test_image5 = transform(pil_image).cuda().unsqueeze(0)
    #         # Dự đoán với mô hình
    #         with torch.no_grad():
    #             features5 = backbone(test_image5)
    #         # Tính toán khoảng cách
    #         distances5 = torch.cdist(features5, memory_banktr, p=2.0)
    #         dist_score5, dist_score_idxs5 = torch.min(distances5, dim=1)
    #         s_star5 = torch.max(dist_score5)
    #         # Tính điểm bất thường
    #         y_score_image5 = s_star5.cpu().numpy()
    #         y_pred_image5 = 1 * (y_score_image5 >= 11.510721206665039)
    #         class_label = ['GOOD', 'BAD']
    #         results_counter[class_label[y_pred_image5]] += 1
            # In kết quả
            # print(f'File name: {path.name}')
            # print(f'Detective score: {y_score_image5:0.9f}')
            # print(f'Prediction: {class_label[y_pred_image5]}')
            # t7 = time.time()
            # print(f'Once Processing. ({t7 - t6:.3f}s)')
    #Xóa tất cả các tệp trong thư mục ImagesResult
    # shutil.rmtree(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult") 
    

        # Load the image
        # image = cv2.imread(str(path))
        # text = class_label[y_pred_image]
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # cv2.putText(image, text, (10, 30), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

    #     # # Display the image using OpenCV
    #     # cv2.imshow('Image', image)
    #     # cv2.waitKey(0)
    #     # cv2.destroyAllWindows()
    #     t7 = time.time()
    #     print(f'Once Processing. ({t7 - t6:.3f}s)')
    # t5 = time.time()
    # print(f'Processing Finished. ({t5 - t2:.3f}s)')

    # print(f"GOOD: {results_counter['GOOD']}")
    # print(f"BAD: {results_counter['BAD']}")
    # #xoa tat ca cac file trong thu muc ImagesResult và addgood
    # #shutil.rmtree(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult")
    # #shutil.rmtree(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\addgood")
    # #os.makedirs(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\ImagesResult")
    # #os.makedirs(r"H:\APP UNIVERSITY\CODE PYTHON\CVWembley\addgood")
    # print("Các tệp đã được xóa thành công.")


