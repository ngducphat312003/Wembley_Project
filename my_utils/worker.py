from PyQt6.QtCore import QThread, pyqtSignal, Qt
import torch
import cv2
from PIL import Image

class Worker(QThread):
    finished = pyqtSignal(list,list)
    def __init__(self, folder_path, transform, backbone, pca, storage_feature_final):
        super().__init__()
        self.folder_path = folder_path
        self.transform = transform
        self.backbone = backbone
        self.pca = pca
        self.storage_feature_final = storage_feature_final
    def run(self):
        y_score1 = []
        y_true1 = []
        for classes in ['good','bad']:
            folder_path1 = self.folder_path / classes
            for pth in folder_path1.glob('*.bmp'):
                class_label = pth.parts[-2]
                with torch.no_grad():
                    img = cv2.imread(pth)
                    pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    data = self.transform(pil_image).cuda().unsqueeze(0)
                    features1 = self.backbone(data)
                    features1_np = features1.cpu().numpy()
                    features1_pca = self.pca.transform(features1_np)  # Không dùng .fit_transform ở đây!
                    features1_pca_tensor = torch.tensor(features1_pca).cuda()
                distances1 = torch.cdist(features1_pca_tensor, self.storage_feature_final, p=2.0)
                dist_score1, dist_score_idxs = torch.min(distances1, dim=1)
                s_star1 = torch.max(dist_score1)
                y_score1.append(s_star1.cpu().numpy())
                y_true1.append(0 if class_label == 'good' else 1)
        self.finished.emit(y_score1, y_true1)