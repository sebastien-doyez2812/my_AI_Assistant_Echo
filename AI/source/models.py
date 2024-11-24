import torch
import torch.nn as nn


####################################
#     Clothes classification :     #
####################################

class clothes_network_LeNet5(nn.Module):
    """
    DEFS:
    ----

    LeNet5 network used
    """
    NUMBER_OF_CLASSES = 10

    def __init__(self, num_classes):
        super().__init__()
        self.layer1 = nn.Sequential(nn.Conv2d(1, 6, kernel_size=5, stride=1, padding=0),
                                     nn.BatchNorm2d(6),
                                     nn.ReLU(),
                                     nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer2 = nn.Sequential(nn.Conv2d(6, 16, kernel_size=5, stride=1, padding=0),
                                     nn.BatchNorm2d(16),
                                     nn.ReLU(),
                                     nn.MaxPool2d(kernel_size=2, stride=2))
        self.fc = nn.Linear(400, 120)  # 400 = 16 * 5 * 5
        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(120, 84)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(84, num_classes)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc(out)
        out = self.relu(out)
        out = self.fc1(out)
        out = self.relu1(out)
        return self.fc2(out)
        
    # Labels used:
    cloths_labels_map={
        0: 'T-shirt',
        1: 'Trouser',
        2: 'Pullover',
        3: 'Dress',
        4: 'Coat',
        5: 'Sandal',
        6: 'Shirt',
        7: 'Sneaker',
        8: 'Bag',
        9: 'Ankle Boot',
    }