"""
AI Model loader and predictor for tomato disease detection
Two models:
  1. leaf_validator.h5  — binary: is this a tomato leaf? (yes/no)
  2. tomato_model.h5    — disease: which of 10 diseases?

University of Rwanda - Final Year Project 2026
"""

import os
import json
import numpy as np
from PIL import Image
import io

MODEL_PATH             = os.path.join(os.path.dirname(__file__), "../../ai_model/tomato_model.h5")
LABELS_PATH            = os.path.join(os.path.dirname(__file__), "../../ai_model/class_labels.json")
VALIDATOR_PATH         = os.path.join(os.path.dirname(__file__), "../../ai_model/leaf_validator.h5")
VALIDATOR_CLASSES_PATH = os.path.join(os.path.dirname(__file__), "../../ai_model/leaf_validator_classes.json")

# Loaded once at startup
_model           = None
_class_labels    = None
_leaf_validator  = None
_tomato_class_idx = 0   # index for "tomato_leaf" in binary model

DISEASE_INFO = {
    "Tomato_healthy": {
        "display_name": "Healthy",
        "is_healthy": True,
        "severity": "none",
        "treatment": "No treatment needed. Your plant looks healthy!",
        "description": "The plant shows no signs of disease."
    },
    "Tomato_Early_blight": {
        "display_name": "Early Blight",
        "is_healthy": False,
        "severity": "medium",
        "treatment": "Apply copper-based fungicide or mancozeb. Remove and destroy infected leaves. Improve air circulation.",
        "description": "Fungal disease causing dark spots with concentric rings on leaves."
    },
    "Tomato_Late_blight": {
        "display_name": "Late Blight",
        "is_healthy": False,
        "severity": "critical",
        "treatment": "Apply metalaxyl or cymoxanil fungicide immediately. Remove all infected plant parts urgently.",
        "description": "Highly destructive disease that can destroy entire crops within days."
    },
    "Tomato_Leaf_Mold": {
        "display_name": "Leaf Mold",
        "is_healthy": False,
        "severity": "medium",
        "treatment": "Improve ventilation. Reduce humidity. Apply fungicide containing chlorothalonil.",
        "description": "Fungal disease causing yellow patches and mold on leaves."
    },
    "Tomato_Septoria_leaf_spot": {
        "display_name": "Septoria Leaf Spot",
        "is_healthy": False,
        "severity": "medium",
        "treatment": "Apply chlorothalonil or copper-based fungicide. Remove affected leaves.",
        "description": "Fungal disease causing small circular spots with dark borders."
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "display_name": "Spider Mites",
        "is_healthy": False,
        "severity": "high",
        "treatment": "Apply miticide or neem oil spray. Increase humidity. Remove heavily infested leaves.",
        "description": "Pest infestation causing stippling and yellowing of leaves."
    },
    "Tomato__Target_Spot": {
        "display_name": "Target Spot",
        "is_healthy": False,
        "severity": "medium",
        "treatment": "Apply fungicide containing azoxystrobin. Remove and destroy infected leaves.",
        "description": "Fungal disease causing circular lesions with target-like rings."
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "display_name": "Yellow Leaf Curl Virus",
        "is_healthy": False,
        "severity": "high",
        "treatment": "No chemical cure. Remove infected plants immediately. Control whitefly with insecticide.",
        "description": "Viral disease spread by whiteflies causing leaf curling and yellowing."
    },
    "Tomato__Tomato_mosaic_virus": {
        "display_name": "Mosaic Virus",
        "is_healthy": False,
        "severity": "high",
        "treatment": "No cure. Remove and destroy infected plants. Disinfect tools between plants.",
        "description": "Viral disease causing mosaic pattern of light and dark green on leaves."
    },
    "Tomato_Bacterial_spot": {
        "display_name": "Bacterial Spot",
        "is_healthy": False,
        "severity": "high",
        "treatment": "Apply copper-based bactericide. Avoid overhead irrigation. Remove infected leaves.",
        "description": "Bacterial disease causing small dark spots on leaves and fruits."
    },
}


def load_model():
    """Load both models into memory once at startup"""
    global _model, _class_labels, _leaf_validator, _tomato_class_idx

    if _model is not None:
        return True

    try:
        import tensorflow as tf

        # ── Disease detection model ──────────────────────────
        model_path  = os.path.abspath(MODEL_PATH)
        labels_path = os.path.abspath(LABELS_PATH)

        if not os.path.exists(model_path):
            print(f"[AI] Disease model not found: {model_path}")
            return False

        print("[AI] Loading tomato disease model...")
        _model = tf.keras.models.load_model(model_path)
        with open(labels_path) as f:
            _class_labels = json.load(f)
        print(f"[AI] Disease model loaded. Classes: {len(_class_labels)}")

        # ── Binary leaf validator ────────────────────────────
        validator_path = os.path.abspath(VALIDATOR_PATH)
        validator_classes_path = os.path.abspath(VALIDATOR_CLASSES_PATH)

        if os.path.exists(validator_path) and os.path.exists(validator_classes_path):
            print("[AI] Loading binary tomato leaf validator...")
            _leaf_validator = tf.keras.models.load_model(validator_path)
            with open(validator_classes_path) as f:
                classes = json.load(f)
            # Find the index for "tomato_leaf" class
            _tomato_class_idx = classes.get("tomato_leaf", 0)
            print(f"[AI] Leaf validator loaded. tomato_leaf index: {_tomato_class_idx}")
        else:
            print("[AI] Leaf validator not found — skipping validation (train it with train_leaf_validator.py)")

        return True

    except Exception as e:
        print(f"[AI] Failed to load model: {e}")
        return False


def is_tomato_leaf(image_bytes: bytes) -> tuple[bool, float]:
    """
    Check if image is a tomato leaf using binary classifier.
    Returns (is_tomato: bool, confidence: float)
    If validator not loaded, returns (True, 100.0) to skip check.
    """
    if _leaf_validator is None:
        return True, 100.0

    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = _leaf_validator.predict(img_array, verbose=0)[0][0]

    # prediction is sigmoid output:
    # close to 0 = tomato_leaf (if tomato_leaf is class 0)
    # close to 1 = not_tomato  (if not_tomato is class 1)
    # Depends on class_indices order from training

    if _tomato_class_idx == 0:
        # tomato_leaf = class 0 → low sigmoid = tomato
        is_tomato = prediction < 0.5
        confidence = (1.0 - float(prediction)) * 100
    else:
        # tomato_leaf = class 1 → high sigmoid = tomato
        is_tomato = prediction >= 0.5
        confidence = float(prediction) * 100

    return is_tomato, round(confidence, 2)


def predict_disease(image_bytes: bytes) -> dict:
    """
    Run disease prediction on image bytes.
    Returns dict with disease name, confidence, severity, treatment.
    """
    if _model is None:
        raise RuntimeError("Model not loaded")

    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = _model.predict(img_array, verbose=0)
    confidence  = float(np.max(predictions)) * 100
    class_idx   = str(int(np.argmax(predictions)))
    class_name  = _class_labels.get(class_idx, "Unknown")

    info = DISEASE_INFO.get(class_name, {
        "display_name": class_name,
        "is_healthy": False,
        "severity": "medium",
        "treatment": "Consult an agronomist for specific treatment.",
        "description": "Disease detected."
    })

    return {
        "disease_name":    info["display_name"],
        "raw_class":       class_name,
        "confidence_score": round(confidence, 2),
        "is_healthy":      info["is_healthy"],
        "severity":        info["severity"],
        "treatment":       info["treatment"],
        "description":     info["description"],
    }
