"""
Evaluate the trained tomato disease model on the validation set.
Produces the REAL confusion matrix and per-class precision/recall
for the thesis (Table 5.2 and Figure 5.3).

This script is READ-ONLY: it loads the already-trained tomato_model.h5
and the same dataset folder used by train_model.py. It does not change,
retrain, or overwrite any model or existing file. It only writes two new
output files (confusion_matrix.csv, per_class_metrics.csv) and, if
matplotlib is available, a confusion_matrix.png.

Run from the ai_model folder:
    cd backend/ai_model
    python evaluate_model.py

University of Rwanda - Final Year Project 2026
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ─── CONFIG (matches train_model.py) ────────────────────────
DATASET_PATH = "dataset/PlantVillage"
MODEL_PATH   = "tomato_model.h5"
LABELS_PATH  = "class_labels.json"
IMG_SIZE     = 224
BATCH_SIZE   = 32
VAL_SPLIT    = 0.2   # same 20% validation split used in training

# Folder name -> friendly display name (for readable tables)
DISPLAY_NAMES = {
    "Tomato_Bacterial_spot": "Bacterial Spot",
    "Tomato_Early_blight": "Early Blight",
    "Tomato_Late_blight": "Late Blight",
    "Tomato_Leaf_Mold": "Leaf Mold",
    "Tomato_Septoria_leaf_spot": "Septoria Leaf Spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Spider Mites",
    "Tomato__Target_Spot": "Target Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Yellow Leaf Curl Virus",
    "Tomato__Tomato_mosaic_virus": "Mosaic Virus",
    "Tomato_healthy": "Healthy",
}


def main():
    # ── 1. Rebuild the SAME validation set (no augmentation, just rescale) ──
    print("\n[1/4] Loading validation set (same 20% split as training)...")
    tomato_folders = sorted(
        f for f in os.listdir(DATASET_PATH)
        if f.lower().startswith("tomato")
    )

    val_datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=VAL_SPLIT)
    val_gen = val_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        classes=tomato_folders,
        shuffle=False,          # MUST be False so labels line up with predictions
    )

    # index -> folder name
    idx_to_folder = {v: k for k, v in val_gen.class_indices.items()}
    class_order = [idx_to_folder[i] for i in range(len(idx_to_folder))]
    display_order = [DISPLAY_NAMES.get(c, c) for c in class_order]
    n = len(class_order)
    print(f"Classes ({n}): {display_order}")
    print(f"Validation images: {val_gen.samples}")

    # ── 2. Load model and predict ──────────────────────────────
    print("\n[2/4] Loading model and running predictions...")
    model = tf.keras.models.load_model(MODEL_PATH)
    probs = model.predict(val_gen, verbose=1)
    y_pred = np.argmax(probs, axis=1)
    y_true = val_gen.classes[: len(y_pred)]

    # ── 3. Confusion matrix + per-class metrics (pure numpy) ───
    print("\n[3/4] Computing confusion matrix and per-class metrics...")
    cm = np.zeros((n, n), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1

    total = cm.sum()
    correct = np.trace(cm)
    overall_acc = correct / total * 100

    precision = np.zeros(n)
    recall = np.zeros(n)
    support = cm.sum(axis=1)
    for i in range(n):
        col = cm[:, i].sum()   # predicted as i
        row = cm[i, :].sum()   # actually i
        precision[i] = cm[i, i] / col * 100 if col else 0.0
        recall[i] = cm[i, i] / row * 100 if row else 0.0

    # weighted averages (by support)
    w_prec = np.average(precision, weights=support)
    w_rec = np.average(recall, weights=support)

    # ── 4. Print results ───────────────────────────────────────
    print("\n" + "=" * 70)
    print("PER-CLASS PRECISION & RECALL (validation set)")
    print("=" * 70)
    print(f"{'Class':<26}{'Precision %':>12}{'Recall %':>12}{'Val Images':>13}")
    print("-" * 70)
    for i in range(n):
        print(f"{display_order[i]:<26}{precision[i]:>12.1f}{recall[i]:>12.1f}{support[i]:>13}")
    print("-" * 70)
    print(f"{'Overall (weighted avg)':<26}{w_prec:>12.1f}{w_rec:>12.1f}{total:>13}")
    print(f"\nOverall validation accuracy: {overall_acc:.2f}%")

    print("\nCONFUSION MATRIX (rows = actual, cols = predicted)")
    header = "".join(f"{i:>6}" for i in range(n))
    print(f"{'':<26}{header}")
    for i in range(n):
        row = "".join(f"{cm[i, j]:>6}" for j in range(n))
        print(f"{display_order[i]:<26}{row}")
    print("\n(Column index key:)")
    for i in range(n):
        print(f"  {i} = {display_order[i]}")

    # ── 5. Save CSV outputs for the thesis ─────────────────────
    with open("per_class_metrics.csv", "w") as f:
        f.write("Class,Precision %,Recall %,Val Images\n")
        for i in range(n):
            f.write(f"{display_order[i]},{precision[i]:.1f},{recall[i]:.1f},{support[i]}\n")
        f.write(f"Overall (weighted avg),{w_prec:.1f},{w_rec:.1f},{total}\n")

    with open("confusion_matrix.csv", "w") as f:
        f.write("actual\\predicted," + ",".join(display_order) + "\n")
        for i in range(n):
            f.write(display_order[i] + "," + ",".join(str(cm[i, j]) for j in range(n)) + "\n")

    print("\n[4/4] Saved: per_class_metrics.csv, confusion_matrix.csv")

    # Optional: save a confusion matrix image (Figure 5.3) if matplotlib exists
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 8))
        im = ax.imshow(cm, cmap="Blues")
        ax.set_xticks(range(n)); ax.set_yticks(range(n))
        ax.set_xticklabels(display_order, rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(display_order, fontsize=8)
        ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
        ax.set_title(f"Confusion Matrix — Disease Classifier ({overall_acc:.1f}% accuracy)")
        for i in range(n):
            for j in range(n):
                ax.text(j, i, cm[i, j], ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=7)
        fig.colorbar(im)
        fig.tight_layout()
        fig.savefig("confusion_matrix.png", dpi=150)
        print("Saved: confusion_matrix.png (use as Figure 5.3)")
    except Exception as e:
        print(f"(Skipped PNG — matplotlib not available: {e})")

    print("\nDONE. Use these REAL numbers in Table 5.2 and Figure 5.3.\n")


if __name__ == "__main__":
    main()
