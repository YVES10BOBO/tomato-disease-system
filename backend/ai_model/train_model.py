"""
Tomato Disease Detection - Model Training Script
Uses MobileNetV2 (transfer learning) on PlantVillage dataset
University of Rwanda - Final Year Project 2026
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import json

# ─── CONFIG ─────────────────────────────────────────────────
DATASET_PATH = "dataset/PlantVillage"
MODEL_OUTPUT  = "tomato_model.h5"
LABELS_OUTPUT = "class_labels.json"
IMG_SIZE      = 224       # MobileNetV2 expects 224x224
BATCH_SIZE    = 32
EPOCHS        = 20
IMG_SHAPE     = (IMG_SIZE, IMG_SIZE, 3)

# ─── STEP 1: FIND TOMATO FOLDERS ONLY ───────────────────────
print("\n[1/5] Scanning dataset for Tomato classes...")

all_folders = os.listdir(DATASET_PATH)
tomato_folders = [f for f in all_folders if f.lower().startswith("tomato")]

print(f"Found {len(tomato_folders)} tomato classes:")
for f in sorted(tomato_folders):
    count = len(os.listdir(os.path.join(DATASET_PATH, f)))
    print(f"  {f}: {count} images")

# ─── STEP 2: CREATE TEMP DATASET WITH ONLY TOMATO ───────────
# We point ImageDataGenerator to the full PlantVillage folder
# but filter only Tomato classes via class_mode

print("\n[2/5] Preparing image data generators...")

# Data augmentation for training (makes model more robust)
train_datagen = ImageDataGenerator(
    rescale=1./255,           # normalize pixel values 0-1
    rotation_range=20,        # randomly rotate images
    width_shift_range=0.2,    # randomly shift horizontally
    height_shift_range=0.2,   # randomly shift vertically
    shear_range=0.2,          # shear transformation
    zoom_range=0.2,           # random zoom
    horizontal_flip=True,     # flip left-right
    validation_split=0.2      # 20% for validation
)

train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    classes=sorted(tomato_folders),   # only tomato folders
    shuffle=True
)

val_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    classes=sorted(tomato_folders),
    shuffle=False
)

num_classes = len(tomato_folders)
print(f"\nTraining samples: {train_generator.samples}")
print(f"Validation samples: {val_generator.samples}")
print(f"Number of classes: {num_classes}")

# ─── STEP 3: BUILD MODEL (Transfer Learning) ────────────────
print("\n[3/5] Building MobileNetV2 model...")

# Load MobileNetV2 pretrained on ImageNet (without top layer)
# This gives us a powerful feature extractor for free
base_model = MobileNetV2(
    input_shape=IMG_SHAPE,
    include_top=False,        # remove ImageNet classification head
    weights='imagenet'        # use pretrained weights
)

# Freeze base model layers (don't retrain them)
base_model.trainable = False

# Add our own classification head for tomato diseases
x = base_model.output
x = GlobalAveragePooling2D()(x)        # reduce feature maps to 1D
x = Dense(128, activation='relu')(x)   # fully connected layer
x = Dropout(0.3)(x)                    # prevent overfitting
predictions = Dense(num_classes, activation='softmax')(x)  # output layer

model = Model(inputs=base_model.input, outputs=predictions)

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"Model ready. Total parameters: {model.count_params():,}")

# ─── STEP 4: TRAIN ──────────────────────────────────────────
print("\n[4/5] Training model...")
print("This will take 30-60 minutes. Do not close the terminal.\n")

callbacks = [
    # Save best model automatically
    ModelCheckpoint(
        MODEL_OUTPUT,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    # Stop early if no improvement for 5 epochs
    EarlyStopping(
        monitor='val_accuracy',
        patience=5,
        restore_best_weights=True,
        verbose=1
    )
]

history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=callbacks,
    verbose=1
)

# ─── STEP 5: SAVE CLASS LABELS ──────────────────────────────
print("\n[5/5] Saving class labels...")

# Map index → class name for predictions
class_labels = {str(v): k for k, v in train_generator.class_indices.items()}

with open(LABELS_OUTPUT, 'w') as f:
    json.dump(class_labels, f, indent=2)

print(f"Class labels saved to {LABELS_OUTPUT}")

# ─── FINAL REPORT ───────────────────────────────────────────
final_acc = max(history.history['val_accuracy']) * 100
print(f"\n{'='*50}")
print(f"TRAINING COMPLETE")
print(f"Best validation accuracy: {final_acc:.1f}%")
print(f"Model saved to: {MODEL_OUTPUT}")
print(f"Labels saved to: {LABELS_OUTPUT}")
print(f"{'='*50}")
print("\nNext step: run the backend and test with: python test_model.py")
