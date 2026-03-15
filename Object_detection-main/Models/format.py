import torch

# Load the model
model_path = "best.pt"  # adjust path
model = torch.load(model_path)  # load on CPU

# Access state_dict (contains all weights)
state_dict = model['model'].state_dict() if 'model' in model else model.state_dict()

# Check dtype of each layer
for name, param in state_dict.items():
    print(name, param.dtype, param.shape)
