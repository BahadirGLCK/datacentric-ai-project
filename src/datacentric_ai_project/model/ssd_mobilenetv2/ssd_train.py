import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from datacentric_ai_project.model.ssd_mobilenetv2.ssd_model import SSDModelWithAnchorsAndNMS
from datacentric_ai_project.mlflow_utils import MLflowHelper  # Assuming MLflow logging is implemented
from datacentric_ai_project.data.bucket.handler import MinIOClient  # Import your MinIO client implementation
from datacentric_ai_project.data.database.handler import DatabaseManager  # Import your database connector
from datacentric_ai_project.data.dataset import AnnotationParser  # Import the annotation parser
from datacentric_ai_project.data.dataset import SSDSimpleDataset  # Import the updated dataset class

class SSDTrainer:
    def __init__(self, model, train_loader,val_loader, criterion, optimizer, device="cuda"):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device

    def train_one_epoch(self, epoch, mlflow_helper):
        self.model.train()
        running_loss = 0.0
        for i, (images, targets) in enumerate(self.train_loader):
            images = torch.stack(images).to(self.device)  # Convert list of tensors to a single tensor
            targets = [{k: v.to(self.device) for k, v in t.items()} for t in targets]

            self.optimizer.zero_grad()
            loc_preds, cls_preds = self.model(images)
            loss = self.criterion(loc_preds, cls_preds, targets)
            loss.backward()
            self.optimizer.step()

            running_loss += loss.item()
            if (i + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}], Step [{i+1}/{len(self.train_loader)}], Loss: {loss.item():.4f}")
        
        avg_loss = running_loss / len(self.train_loader)
        mlflow_helper.log_metric("train_loss", avg_loss, step=epoch)
        return avg_loss

    def evaluate(self, epoch, mlflow_helper):
        self.model.eval()
        total_map = 0.0  # Placeholder for mAP
        with torch.no_grad():
            for images, targets in self.val_loader:
                images, targets = images.to(self.device), [{k: v.to(self.device) for k, v in t.items()} for t in targets]
                loc_preds, cls_preds = self.model(images)

                # Placeholder for mAP calculation; replace with your actual mAP computation
                mAP = compute_mAP(loc_preds, cls_preds, targets)  
                total_map += mAP
        
        avg_map = total_map / len(self.val_loader)
        mlflow_helper.log_metric("mAP", avg_map, step=epoch)
        print(f"Validation mAP: {avg_map:.4f}")
        return avg_map

    def save_checkpoint(self, epoch):
        checkpoint_path = f"checkpoints/ssd_mobilenetv2_epoch_{epoch+1}.pth"
        torch.save(self.model.state_dict(), checkpoint_path)
        print(f"Checkpoint saved: {checkpoint_path}")
        return checkpoint_path

    def train(self, num_epochs, mlflow_helper):
        for epoch in range(num_epochs):
            train_loss = self.train_one_epoch(epoch, mlflow_helper)
            print(f"Epoch [{epoch+1}/{num_epochs}] Training Loss: {train_loss:.4f}")

            # Evaluate and log mAP at the end of each epoch
            val_map = self.evaluate(epoch, mlflow_helper)
            print(f"Epoch [{epoch+1}/{num_epochs}] Validation mAP: {val_map:.4f}")

            # Save model checkpoint after each epoch
            checkpoint_path = self.save_checkpoint(epoch)
            mlflow_helper.log_artifact(checkpoint_path)
        
        # Save the final model
        mlflow_helper.log_model(self.model, path="final_model")
        print("Training complete. Final model saved.")

# Utility function to initialize model, optimizer, and loss function
def initialize_training(num_classes, learning_rate):
    model = SSDModelWithAnchorsAndNMS(num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()  # Replace with a suitable SSD loss function
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9, weight_decay=0.0005)
    return model, criterion, optimizer

def collate_fn(batch):
    images, targets = zip(*batch)
    return list(images), list(targets)

# Main entry point
def main():
    # Training configurations
    num_classes = 3
    learning_rate = 0.001
    batch_size = 16
    num_epochs = 10

    # Initialize MLflow helper
    mlflow_helper = MLflowHelper("Object Detection", "SSD MobileNetV2 Training")
    mlflow_helper.start_run(params={"learning_rate": learning_rate, "epochs": num_epochs, "batch_size": batch_size})

    # Initialize Datasets and DataLoaders
    train_dataset = SSDSimpleDataset(transform=None)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)

    # Initialize model, criterion, and optimizer
    model, criterion, optimizer = initialize_training(num_classes, learning_rate)
    val_loader = None
    # Initialize trainer and train the model
    trainer = SSDTrainer(model, train_loader, val_loader, criterion, optimizer, device="mps")
    trainer.train(num_epochs, mlflow_helper)

    mlflow_helper.end_run()

if __name__ == "__main__":
    main()