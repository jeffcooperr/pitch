import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import ImageFolder
import os

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Data transforms
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load dataset
dataset = ImageFolder(root='./training_data', transform=transform)
print(f"Dataset size: {len(dataset)}")
print(f"Classes: {dataset.classes}")

# Split into train/validation
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

# Model setup
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

# Freeze pre-trained layers
for param in model.parameters():
    param.requires_grad = False

# Replace final layer for binary classification
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 1)
model = model.to(device)

# Loss function and optimizer
criterion = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.fc.parameters(), lr=LEARNING_RATE)

# Training loop
best_val_loss = float('inf')
for epoch in range(EPOCHS):
    # Training phase
    model.train()
    train_loss = 0.0
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs).squeeze()
        loss = criterion(outputs, labels.float())
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    
    # Validation phase
    model.eval()
    val_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs).squeeze()
            loss = criterion(outputs, labels.float())
            val_loss += loss.item()
            
            # Calculate accuracy
            predicted = (outputs > 0).float()
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    train_loss /= len(train_loader)
    val_loss /= len(val_loader)
    accuracy = 100 * correct / total
    
    print(f'Epoch {epoch+1}/{EPOCHS}:')
    print(f'  Train Loss: {train_loss:.4f}')
    print(f'  Val Loss: {val_loss:.4f}')
    print(f'  Val Accuracy: {accuracy:.2f}%')
    
    # Save best model
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'best_pitch_classifier.pth')
        print(f'  Saved best model (val_loss: {val_loss:.4f})')
    print()

print("Training completed!")
