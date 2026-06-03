"""
Deep Knowledge Tracing — TensorFlow LSTM Model Definition
Training script: ml/training/train_dkt.py
"""
import numpy as np
from typing import Tuple


def build_dkt_model(num_skills: int = 500, hidden_units: int = 200):
    """
    Build LSTM-based DKT model.
    
    Input:  (batch, seq_len, num_skills * 2)  — one-hot encoded (skill, correct) pairs
    Output: (batch, seq_len, num_skills)       — P(correct | next attempt on each skill)
    """
    try:
        import tensorflow as tf
        inputs  = tf.keras.Input(shape=(None, num_skills * 2), name="interaction_sequence")
        x       = tf.keras.layers.LSTM(hidden_units, return_sequences=True, name="lstm_1")(inputs)
        x       = tf.keras.layers.Dropout(0.3)(x)
        x       = tf.keras.layers.LSTM(hidden_units // 2, return_sequences=True, name="lstm_2")(x)
        x       = tf.keras.layers.Dropout(0.2)(x)
        outputs = tf.keras.layers.Dense(num_skills, activation="sigmoid", name="mastery_output")(x)
        model   = tf.keras.Model(inputs, outputs, name="DKT")
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
            loss="binary_crossentropy",
            metrics=["AUC", "accuracy"],
        )
        return model
    except ImportError:
        print("TensorFlow not installed. Install with: pip install tensorflow==2.13.0")
        return None


def generate_synthetic_data(
    num_students: int = 500,
    num_skills: int = 50,
    seq_len: int = 100,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic student interaction data for DKT training.
    Simulates students with varying skill levels and learning rates.
    """
    X = np.zeros((num_students, seq_len, num_skills * 2), dtype=np.float32)
    y = np.zeros((num_students, seq_len, num_skills), dtype=np.float32)

    for student in range(num_students):
        mastery = np.random.beta(2, 5, num_skills)  # Most students start low
        learn_rate = np.random.uniform(0.05, 0.25, num_skills)

        for t in range(seq_len):
            skill = np.random.randint(0, num_skills)
            p_correct = mastery[skill] * (1 - 0.1) + (1 - mastery[skill]) * 0.2  # slip + guess
            correct = int(np.random.random() < p_correct)

            offset = skill + (num_skills if correct else 0)
            X[student, t, offset] = 1.0
            y[student, t, :] = mastery

            # Learning update
            if correct:
                mastery[skill] = min(0.99, mastery[skill] + learn_rate[skill])

    return X, y


if __name__ == "__main__":
    print("Building DKT model...")
    model = build_dkt_model(num_skills=50)
    if model:
        model.summary()
        print("\nGenerating synthetic training data...")
        X, y = generate_synthetic_data(num_students=200, num_skills=50, seq_len=50)
        print(f"X shape: {X.shape}, y shape: {y.shape}")
        print("\nTraining DKT (5 epochs demo)...")
        model.fit(X, y, epochs=5, batch_size=32, validation_split=0.2, verbose=1)
        model.save("saved_model")
        print("Model saved to ml/models/dkt/saved_model")
