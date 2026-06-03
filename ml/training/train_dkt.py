"""DKT Training Script — run from project root: python ml/training/train_dkt.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from ml.models.dkt.model import build_dkt_model, generate_synthetic_data
import numpy as np

NUM_SKILLS   = 500
NUM_STUDENTS = 2000
SEQ_LEN      = 150
EPOCHS       = 30
BATCH_SIZE   = 64

print("=" * 60)
print("AMILE — Deep Knowledge Tracing Training")
print("=" * 60)

model = build_dkt_model(num_skills=NUM_SKILLS)
if model is None:
    print("ERROR: TensorFlow not available.")
    sys.exit(1)

print(f"\nGenerating {NUM_STUDENTS} synthetic student sequences...")
X, y = generate_synthetic_data(NUM_STUDENTS, NUM_SKILLS, SEQ_LEN)
print(f"Data shape — X: {X.shape}, y: {y.shape}")

try:
    import tensorflow as tf
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint("ml/models/dkt/saved_model", save_best_only=True),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3),
        tf.keras.callbacks.TensorBoard(log_dir="ml/logs/dkt"),
    ]
    history = model.fit(
        X, y,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        callbacks=callbacks,
        verbose=1,
    )
    print(f"\nTraining complete. Best val AUC: {max(history.history.get('val_auc', [0])):.4f}")
except Exception as e:
    print(f"Training error: {e}")
