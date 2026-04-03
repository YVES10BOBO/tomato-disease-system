"""
Test the trained tomato disease model on a single image
Usage: python test_model.py --image path/to/leaf.jpg
"""

import sys
import json
import numpy as np
import tensorflow as tf
from PIL import Image

MODEL_PATH = "tomato_model.h5"
LABELS_PATH = "class_labels.json"
IMG_SIZE = 224

# Disease info for display
DISEASE_INFO = {
    "Tomato_healthy": {
        "display": "Healthy",
        "severity": "none",
        "treatment": "No treatment needed. Plant looks healthy!"
    },
    "Tomato_Early_blight": {
        "display": "Early Blight",
        "severity": "medium",
        "treatment": "Apply copper-based fungicide or mancozeb. Remove infected leaves."
    },
    "Tomato_Late_blight": {
        "display": "Late Blight",
        "severity": "critical",
        "treatment": "Apply metalaxyl fungicide immediately. Remove all infected parts urgently."
    },
    "Tomato_Leaf_Mold": {
        "display": "Leaf Mold",
        "severity": "medium",
        "treatment": "Improve ventilation. Apply fungicide containing chlorothalonil."
    },
    "Tomato_Septoria_leaf_spot": {
        "display": "Septoria Leaf Spot",
        "severity": "medium",
        "treatment": "Apply chlorothalonil fungicide. Remove affected leaves."
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "display": "Spider Mites",
        "severity": "high",
        "treatment": "Apply miticide or neem oil. Increase humidity around plants."
    },
    "Tomato__Target_Spot": {
        "display": "Target Spot",
        "severity": "medium",
        "treatment": "Apply fungicide. Remove infected leaves and destroy them."
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "display": "Yellow Leaf Curl Virus",
        "severity": "high",
        "treatment": "No cure. Remove infected plants. Control whitefly population."
    },
    "Tomato__Tomato_mosaic_virus": {
        "display": "Mosaic Virus",
        "severity": "high",
        "treatment": "No cure. Remove infected plants. Disinfect tools between plants."
    },
    "Tomato_Bacterial_spot": {
        "display": "Bacterial Spot",
        "severity": "high",
        "treatment": "Apply copper bactericide. Avoid overhead irrigation."
    },
}


def predict(image_path):
    print(f"Loading model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)

    with open(LABELS_PATH) as f:
        class_labels = json.load(f)

    print(f"Analyzing image: {image_path}")
    img = Image.open(image_path).convert('RGB')
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array, verbose=0)
    confidence = float(np.max(predictions)) * 100
    class_idx = str(np.argmax(predictions))
    class_name = class_labels[class_idx]

    info = DISEASE_INFO.get(class_name, {
        "display": class_name,
        "severity": "unknown",
        "treatment": "Consult an agronomist."
    })

    print(f"\n{'='*40}")
    print(f"Result: {info['display']}")
    print(f"Confidence: {confidence:.1f}%")
    print(f"Severity: {info['severity']}")
    print(f"Treatment: {info['treatment']}")
    print(f"{'='*40}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_model.py --image path/to/leaf.jpg")
    else:
        image_path = sys.argv[sys.argv.index("--image") + 1]
        predict(image_path)
