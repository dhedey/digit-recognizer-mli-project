import torch
import torch.nn as nn
import torch.nn.functional as F
import PIL.Image
from torchvision.transforms import v2

class FirstNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 16, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class DigitModelBase:
    def __init__(self, network):
        self.network = network

    def probabilities(self, pil_image: PIL.Image.Image, temperature: float):
        """
        Expects a 28x28 greyscale image with a white background,
        and returns a list of 10 (digit, probability) tuples.
        """
        transform = input_transform = v2.Compose([
            v2.ToImage(),
            v2.ToDtype(dtype=torch.float32),
        ])
        image_tensor = transform(pil_image)
        # Invert black and white
        ones = torch.full_like(image_tensor, 255.0)
        image_tensor = ones - image_tensor

        if image_tensor.shape != (1, 28, 28):
            raise ValueError("Expected a 28x28 greyscale image")
        singleton_batch = torch.stack([image_tensor])
        logits = self.network(singleton_batch)
        digit_probabilities = [x for x in enumerate(F.softmax(logits * temperature, dim=1)[0].tolist())]
        return digit_probabilities

    def predict(self, pil_image: PIL.Image.Image, temperature: float):
        """
        Expects a 28x28 greyscale image with a white background,
        and returns (predicted_digit, probability)
        """
        return max(self.probabilities(pil_image, temperature), key=lambda x: x[1])

class CenteredDigitModel(DigitModelBase):
    def __init__(self):
        network = FirstNetwork()
        from importlib import resources
        weights = resources.open_binary(__package__, "centered_digit_model_weights.pth")
        network.load_state_dict(torch.load(weights))
        network.eval()
        super().__init__(network)
