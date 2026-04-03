"""
Binary Plant Leaf Validator - Training Script
Trains a model to answer ONE question: "Is this a plant leaf? YES or NO"

Classes:
  0 = plant_leaf  (ALL PlantVillage folders - tomato, pepper, potato)
  1 = not_plant   (buildings, streets, mountains, sea, glaciers)

This stops non-plant objects from being diagnosed with diseases.
Any plant leaf (tomato, pepper, potato) passes through to disease detection.

University of Rwanda - Final Year Project 2026
"""

import os
import shutil
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import json

# ─── CONFIG ──────────────────────────────────────────────────
DATASET_PATH   = "dataset/PlantVillage"
INNER_PATH     = "dataset/PlantVillage/PlantVillage"
NON_PLANT_PATH = "dataset/non_plant"           # Intel image classification
BINARY_DIR     = "dataset/plant_binary_dataset"
MODEL_OUTPUT   = "leaf_validator.h5"
IMG_SIZE       = 224
BATCH_SIZE     = 32
EPOCHS         = 15

# ─── STEP 1: BUILD BINARY DATASET STRUCTURE ─────────────────
print("\n[1/5] Building binary dataset...")

# Create folder structure
tomato_train       = os.path.join(BINARY_DIR, "train", "tomato_leaf")
tomato_val         = os.path.join(BINARY_DIR, "val",   "tomato_leaf")
not_tomato_train   = os.path.join(BINARY_DIR, "train", "not_tomato_leaf")
not_tomato_val     = os.path.join(BINARY_DIR, "val",   "not_tomato_leaf")

for folder in [tomato_train, tomato_val, not_tomato_train, not_tomato_val]:
    os.makedirs(folder, exist_ok=True)


def copy_images(src_folder, dest_train, dest_val, val_split=0.2):
    """Copy images from source to train/val folders"""
    if not os.path.exists(src_folder):
        print(f"  Skipping {src_folder} - not found")
        return 0
    images = [f for f in os.listdir(src_folder)
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    np.random.shuffle(images)
    split = int(len(images) * (1 - val_split))
    train_imgs = images[:split]
    val_imgs   = images[split:]

    for img in train_imgs:
        src = os.path.join(src_folder, img)
        dst = os.path.join(dest_train, f"{os.path.basename(src_folder)}_{img}")
        if not os.path.exists(dst):
            shutil.copy2(src, dst)

    for img in val_imgs:
        src = os.path.join(src_folder, img)
        dst = os.path.join(dest_val, f"{os.path.basename(src_folder)}_{img}")
        if not os.path.exists(dst):
            shutil.copy2(src, dst)

    return len(images)


# ── POSITIVE: TOMATO leaf images only ───────────────────────
print("  Copying tomato leaf images (positive class)...")
tomato_count = 0

for base in [DATASET_PATH, INNER_PATH]:
    if not os.path.exists(base):
        continue
    for folder in os.listdir(base):
        if folder.lower().startswith("tomato"):
            full_path = os.path.join(base, folder)
            if os.path.isdir(full_path):
                count = copy_images(full_path, tomato_train, tomato_val)
                tomato_count += count
                print(f"    {folder}: {count} images")

# ── NEGATIVE: Pepper + Potato + non-plant images ─────────────
print("\n  Copying not-tomato-leaf images (negative class)...")
not_tomato_count = 0

# Other plant leaves (pepper, potato) from PlantVillage
for base in [DATASET_PATH, INNER_PATH]:
    if not os.path.exists(base):
        continue
    for folder in os.listdir(base):
        if not folder.lower().startswith("tomato") and os.path.isdir(os.path.join(base, folder)):
            full_path = os.path.join(base, folder)
            count = copy_images(full_path, not_tomato_train, not_tomato_val)
            not_tomato_count += count
            print(f"    {folder}: {count} images")

# Non-plant images (buildings, streets, mountains etc.)
if os.path.exists(NON_PLANT_PATH):
    for root, dirs, files in os.walk(NON_PLANT_PATH):
        for d in dirs:
            src = os.path.join(root, d)
            count = copy_images(src, not_tomato_train, not_tomato_val)
            not_tomato_count += count
            if count > 0:
                print(f"    {d} (non-plant): {count} images")

print(f"\n  Total tomato leaf images:     {tomato_count}")
print(f"  Total not-tomato-leaf images: {not_tomato_count}")

# ─── STEP 2: DATA GENERATORS ────────────────────────────────
print("\n[2/5] Creating data generators...")

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.3,
    horizontal_flip=True,
    brightness_range=[0.7, 1.3],   # simulate different lighting
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    os.path.join(BINARY_DIR, "train"),
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=True,
    classes=['tomato_leaf', 'not_tomato_leaf']   # 0=tomato_leaf, 1=not_tomato_leaf
)

val_generator = val_datagen.flow_from_directory(
    os.path.join(BINARY_DIR, "val"),
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=False,
    classes=['tomato_leaf', 'not_tomato_leaf']
)

print(f"Training samples:   {train_generator.samples}")
print(f"Validation samples: {val_generator.samples}")
print(f"Class mapping:      {train_generator.class_indices}")

# Save class mapping
with open("leaf_validator_classes.json", "w") as f:
    json.dump(train_generator.class_indices, f, indent=2)

# ─── STEP 3: BUILD MODEL ────────────────────────────────────
print("\n[3/5] Building binary classifier model...")

base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(64, activation='relu')(x)
x = Dropout(0.4)(x)
output = Dense(1, activation='sigmoid')(x)   # binary: 0=tomato, 1=not_tomato

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print(f"Model ready. Parameters: {model.count_params():,}")

# ─── STEP 4: TRAIN ──────────────────────────────────────────
print("\n[4/5] Training binary classifier...")
print("This will take 15-30 minutes.\n")

callbacks = [
    ModelCheckpoint(
        MODEL_OUTPUT,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    EarlyStopping(
        monitor='val_accuracy',
        patience=4,
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

# ─── STEP 5: REPORT ─────────────────────────────────────────
final_acc = max(history.history['val_accuracy']) * 100
print(f"\n{'='*50}")
print(f"TRAINING COMPLETE")
print(f"Best validation accuracy: {final_acc:.1f}%")
print(f"Model saved to: {MODEL_OUTPUT}")
print(f"{'='*50}")
print("\nNext: restart backend to use the new validator")
