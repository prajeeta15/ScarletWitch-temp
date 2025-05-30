import torch
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt

# Load pretrained YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or 'custom' for your own model

def detect_objects(image_path):
    results = model(image_path)
    results.print()  # Print results in console
    results.save()   # Save annotated image
    return results.pandas().xyxy[0]  # return detections as pandas dataframe

# Example usage
detections = detect_objects('darkweb_image.jpg')
print(detections[['name', 'confidence']])
