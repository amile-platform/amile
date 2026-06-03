"""Model evaluation script — AUC, accuracy, and calibration metrics"""
import numpy as np
from typing import Dict


def evaluate_bkt(test_sequences: list) -> Dict:
    """Evaluate BKT model on test sequences."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    from backend.app.services.ai.bkt_service import BKTService
    bkt = BKTService()
    
    all_predicted, all_actual = [], []
    for seq in test_sequences:
        mastery = 0.15
        for interaction in seq[:-1]:
            mastery, _ = bkt.update(mastery, interaction["correct"], "test_skill")
            all_predicted.append(mastery)
            all_actual.append(interaction["correct"])

    if not all_predicted:
        return {"error": "No sequences provided"}

    # Simple AUC approximation
    pairs = sorted(zip(all_predicted, all_actual), reverse=True)
    tp = fp = 0
    pos = sum(a for _, a in pairs)
    neg = len(pairs) - pos
    auc = 0.0
    for _, actual in pairs:
        if actual:
            tp += 1
        else:
            fp += 1
            auc += tp
    auc = auc / (pos * neg) if pos > 0 and neg > 0 else 0.5

    accuracy = sum(1 for p, a in zip(all_predicted, all_actual) if (p > 0.5) == bool(a)) / len(all_predicted)
    return {"bkt_auc": round(auc, 4), "bkt_accuracy": round(accuracy, 4), "n_predictions": len(all_predicted)}


if __name__ == "__main__":
    # Demo evaluation with synthetic data
    import random
    random.seed(42)
    sequences = [
        [{"correct": random.random() > 0.4 + i * 0.05} for i in range(20)]
        for _ in range(100)
    ]
    results = evaluate_bkt(sequences)
    print("BKT Evaluation Results:")
    for k, v in results.items():
        print(f"  {k}: {v}")
