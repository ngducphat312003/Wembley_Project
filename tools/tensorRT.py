import torch

if torch.cuda.is_available():
    print("CUDA is available. Using GPU.")
    print(torch.cuda.current_device())
else:
    print("CUDA is not available. Using CPU.")