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

class AssertShape(nn.Module):
    def __init__(
        self,
        size: tuple | list[int],
        label: str = None,
        ignore_batch_size: bool = True,
    ):
        super().__init__()
        self.size = tuple(size)
        self.ignore_batch_size = ignore_batch_size
        if label is not None:
            self._label_prefix = f"{label}: "
        else:
            self._label_prefix = ""
        self._cached_check_shape = torch.Size(size)
        self._last_batch_size = None

    def forward(self, x):
        if self.ignore_batch_size:
            if self._last_batch_size != x.shape[0]:
                self._cached_check_shape = torch.Size(tuple([x.shape[0],] + [d for d in self.size]))
            if x.shape != self._cached_check_shape:
                raise ValueError(f"{self._label_prefix}Expected tensor shape (*, {", ".join(str(d) for d in self.size)}), got ({", ".join(str(d) for d in x.shape)})")
        else:
            if x.shape != self._cached_check_shape:
                raise ValueError(f"{self._label_prefix}Expected tensor shape ({", ".join(str(d) for d in self.size)}), got ({", ".join(str(d) for d in x.shape)})")
        return x

class SecondNetwork(nn.Module):
    def __init__(self):
        # Inspired by thinking in article:
        # * https://chriswolfvision.medium.com/what-is-translation-equivariance-and-why-do-we-use-convolutions-to-get-it-6f18139d4c59
        # A reproduction of:
        # * https://www.kaggle.com/code/minggyul/digit-recognizer-using-cnn
        super().__init__()
        self.layers = nn.Sequential(
            AssertShape([1, 28, 28]),
            nn.Conv2d(1, 32, kernel_size=3),  # AssertShape([32, 26, 26]),
            nn.ReLU(),
            nn.BatchNorm2d(32),               # AssertShape([32, 26, 26]),
            nn.Conv2d(32, 32, kernel_size=3), # AssertShape([32, 24, 24]),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),               # AssertShape([32, 12, 12]),
            nn.Dropout(0.25),

            nn.Conv2d(32, 64, kernel_size=3), # AssertShape([64, 10, 10]),
            nn.ReLU(),
            nn.BatchNorm2d(64),               # AssertShape([64, 10, 10]),
            nn.Conv2d(64, 64, kernel_size=3), # AssertShape([64, 8, 8]),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),               # AssertShape([64, 4, 4]),
            nn.Dropout(0.25),

            nn.Flatten(),                     # AssertShape([64 * 4 * 4]),
            nn.Linear(64 * 4 * 4, 100),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(100, 10),
        )

    def forward(self, x):
        return self.layers(x)

class DigitModelBase:
    def __init__(self, network):
        self.network = network

    def probabilities(self, pil_image: PIL.Image.Image, temperature: float, scale: bool):
        """
        Expects a 28x28 greyscale image with a white background,
        and returns a list of 10 (digit, probability) tuples.
        """
        transform = v2.Compose([
            v2.ToImage(),
            v2.ToDtype(dtype=torch.float32, scale=scale),
        ])
        image_tensor = transform(pil_image)
        # Invert black and white
        ones = torch.full_like(image_tensor, 1.0 if scale else 255.0)
        image_tensor = ones - image_tensor

        if image_tensor.shape != (1, 28, 28):
            raise ValueError("Expected a 28x28 greyscale image")
        singleton_batch = torch.stack([image_tensor])
        logits = self.network(singleton_batch)
        digit_probabilities = [x for x in enumerate(F.softmax(logits * temperature, dim=1)[0].tolist())]
        return digit_probabilities

    def predict(self, pil_image: PIL.Image.Image, temperature: float, scale: bool):
        """
        Expects a 28x28 greyscale image with a white background,
        and returns (predicted_digit, probability)
        """
        return max(self.probabilities(pil_image, temperature, scale), key=lambda x: x[1])

class FirstModel(DigitModelBase):
    def __init__(self):
        network = FirstNetwork()
        from importlib import resources
        weights = resources.open_binary(__package__, "model_v1.pth")
        network.load_state_dict(torch.load(weights))
        network.eval()
        super().__init__(network)

class SecondModel(DigitModelBase):
    def __init__(self):
        network = SecondNetwork()
        from importlib import resources
        weights = resources.open_binary(__package__, "model_v2.pth")
        network.load_state_dict(torch.load(weights))
        network.eval()
        super().__init__(network)