import torch
import cv2
import numpy as np
from PIL import Image
from torchvision import transforms
from pathlib import Path
import time
from collections import Counter
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from torchvision import models

def setup_ad():
    transform = transforms.Compose([ transforms.Resize((224,224)), transforms.ToTensor() ])

    class mobilenet_feature_extractor(torch.nn.Module):
        def __init__(self):
            super(mobilenet_feature_extractor, self).__init__()
        # Tải mô hình MobileNetV3 với trọng số đã huấn luyện
            self.model = models.mobilenet_v3_large(pretrained=True)

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
    backbone = mobilenet_feature_extractor().cuda()
    memory = torch.load(r"H:\HK242\LVTN\Model\GREYPLASTIC\memory_bank_grey_tr_v3.pt").cuda()
    return transform, backbone, memory
if __name__ == '__main__':
    transform, backbone, memory = setup_ad()
    t1 = time.time()
    backbone.eval()
    results_counter = Counter()
    test_path = Path(r"H:\APP UNIVERSITY\CODE PYTHON\testtr")
    plastic_config = {
            "trplastic_": (memory, 7.191781997680664),
    }
    for plastic, (memory_bank, threshold) in plastic_config.items():
        for path in test_path.glob('*.bmp'):
            file_path = str(path)
            img = cv2.imread(file_path)
            # cv2.imshow("img", img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            test_image = transform(Image.open(path)).cuda().unsqueeze(0)
            with torch.no_grad():
                features = backbone(test_image)
                distances = torch.cdist(features, memory_bank, p=2.0)
                s_star = torch.max(torch.min(distances, dim=1).values)
                y_score_image = s_star.cpu().numpy()
                y_pred_image = 1 * (y_score_image >= threshold)
                class_label = ['GOOD', 'BAD']
                if class_label[y_pred_image] == 'BAD':
                    results_counter[class_label[y_pred_image]] += 1
                    print("Score: ",y_score_image)
                    print("BAD: ",path.name)
                elif class_label[y_pred_image] == 'GOOD':
                    results_counter[class_label[y_pred_image]] += 1
                    print("Score: ",y_score_image)
                    print("GOOD: ",path.name)
    print("Total GOOD: ", results_counter['GOOD'])
    print("Total BAD: ", results_counter['BAD'])
    t2 = time.time()
    print("Time: ", t2-t1)