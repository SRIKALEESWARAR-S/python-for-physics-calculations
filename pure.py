import warnings
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import pennylane as qml

from scipy.special import eval_legendre, jv
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

warnings.filterwarnings('ignore')

# ==========================================
# 1. CONFIGURATION & HYPERPARAMETERS
# ==========================================
N_QUBITS = 4
N_RAW_FEATURES = 4
L_DEG = 2
B_ORD = 2
QNN_LAYERS = 2
EPOCHS = 25
BATCH_SIZE = 32
LEARNING_RATE = 0.05
SEEDS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

EXPANDED_DIM = N_RAW_FEATURES * (1 + L_DEG + B_ORD)  # 20 features

# ==========================================
# 2. FEATURE EXPANSION & DATA HELPERS
# ==========================================
def apply_legendre_bessel_transform(X_scaled):
    X_out = []
    for row in X_scaled:
        expanded_row = []
        for x in row:
            expanded_row.append(x)
            for deg in range(1, L_DEG + 1):
                expanded_row.append(eval_legendre(deg, x))
            for order in range(B_ORD):
                expanded_row.append(jv(order, x))
        X_out.append(expanded_row)
    return np.array(X_out)

def get_data(seed):
    data = load_breast_cancer()
    X_raw = data.data[:, :N_RAW_FEATURES]
    # Invert binary target so 1 = Malignant, 0 = Benign (Standard Clinical Convention)
    y_raw = 1 - data.target

    # Scale raw features to [-1, 1] for quantum embedding
    std_scaler = StandardScaler()
    minmax_scaler = MinMaxScaler(feature_range=(-1, 1))
    X_scaled = minmax_scaler.fit_transform(std_scaler.fit_transform(X_raw))
    
    # Generate functional expansion
    X_expanded = apply_legendre_bessel_transform(X_scaled)

    # Train/Test splits
    splits = train_test_split(
        X_scaled, X_expanded, y_raw, test_size=0.2, random_state=seed, stratify=y_raw
    )
    return splits  # X_raw_tr, X_raw_te, X_exp_tr, X_exp_te, y_tr, y_te

# ==========================================
# 3. PENNYLANE QUANTUM CIRCUITS
# ==========================================
dev = qml.device("default.qubit", wires=N_QUBITS)

# Proposed QNN: Re-uploads 20 expanded features cyclically
@qml.qnode(dev, interface="torch")
def proposed_qnn_circuit(inputs, weights):
    cycles = EXPANDED_DIM // N_QUBITS
    for i in range(cycles):
        feat_slice = inputs[..., i * N_QUBITS : (i + 1) * N_QUBITS]
        rot_axis = 'X' if i % 3 == 0 else ('Y' if i % 3 == 1 else 'Z')
        qml.AngleEmbedding(feat_slice, wires=range(N_QUBITS), rotation=rot_axis)

    for layer in range(weights.shape[0]):
        for q in range(N_QUBITS):
            qml.Rot(weights[layer, q, 0], weights[layer, q, 1], weights[layer, q, 2], wires=q)
        for q in range(N_QUBITS):
            qml.CNOT(wires=[q, (q + 1) % N_QUBITS])

    return qml.expval(qml.PauliZ(0))

# Baseline QNN: Angle Embedding on raw 4 features without expansion
@qml.qnode(dev, interface="torch")
def baseline_qnn_circuit(inputs, weights):
    qml.AngleEmbedding(inputs, wires=range(N_QUBITS), rotation='X')

    for layer in range(weights.shape[0]):
        for q in range(N_QUBITS):
            qml.Rot(weights[layer, q, 0], weights[layer, q, 1], weights[layer, q, 2], wires=q)
        for q in range(N_QUBITS):
            qml.CNOT(wires=[q, (q + 1) % N_QUBITS])

    return qml.expval(qml.PauliZ(0))

# Generic Torch Module wrapper
class HybridQNN(nn.Module):
    def __init__(self, circuit_fn):
        super().__init__()
        weight_shapes = {"weights": (QNN_LAYERS, N_QUBITS, 3)}
        self.qlayer = qml.qnn.TorchLayer(circuit_fn, weight_shapes)
        self.fc = nn.Linear(1, 1)

    def forward(self, x):
        q_out = self.qlayer(x)
        if q_out.dim() == 1:
            q_out = q_out.unsqueeze(1)
        else:
            q_out = q_out.reshape(-1, 1)
        return torch.sigmoid(self.fc(q_out))

# Trainer routine for PyTorch QNN models
def train_eval_qnn(circuit_fn, X_tr, y_tr, X_te, y_te):
    X_tr_t = torch.tensor(X_tr, dtype=torch.float32)
    y_tr_t = torch.tensor(y_tr, dtype=torch.float32).unsqueeze(1)
    X_te_t = torch.tensor(X_te, dtype=torch.float32)

    model = HybridQNN(circuit_fn)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(EPOCHS):
        model.train()
        permutation = torch.randperm(X_tr_t.size()[0])
        for i in range(0, X_tr_t.size()[0], BATCH_SIZE):
            indices = permutation[i : i + BATCH_SIZE]
            batch_x, batch_y = X_tr_t[indices], y_tr_t[indices]

            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        probs = model(X_te_t).cpu().numpy().flatten()
        preds = (probs > 0.5).astype(int)

    acc = accuracy_score(y_te, preds)
    f1 = f1_score(y_te, preds, zero_division=0)
    auc = roc_auc_score(y_te, probs)
    return acc, f1, auc

# ==========================================
# 4. BENCHMARK HARNESS EXECUTION
# ==========================================
models = [
    "SVM (Raw)", "SVM (Legendre-Bessel)",
    "Random Forest (Raw)", "Random Forest (Legendre-Bessel)",
    "MLP (Raw)", "MLP (Legendre-Bessel)",
    "Standard QNN (Raw AngleEmbedding)",
    "Proposed QNN (Legendre-Bessel + PQC)"
]

results = {m: {"acc": [], "f1": [], "auc": []} for m in models}

print("=" * 70)
print(f"RUNNING ABLATION STUDY ACROSS {len(SEEDS)} SEEDS")
print("=" * 70)

for run_idx, seed in enumerate(SEEDS):
    print(f"\n[Seed {run_idx + 1}/{len(SEEDS)}: {seed}]")
    X_raw_tr, X_raw_te, X_exp_tr, X_exp_te, y_tr, y_te = get_data(seed)

    # 1. Classical SVM
    svm_raw = SVC(probability=True, random_state=seed).fit(X_raw_tr, y_tr)
    svm_exp = SVC(probability=True, random_state=seed).fit(X_exp_tr, y_tr)
    
    # 2. Classical Random Forest
    rf_raw = RandomForestClassifier(n_estimators=50, random_state=seed).fit(X_raw_tr, y_tr)
    rf_exp = RandomForestClassifier(n_estimators=50, random_state=seed).fit(X_exp_tr, y_tr)

    # 3. Classical MLP
    mlp_raw = MLPClassifier(hidden_layer_sizes=(16, 8), max_iter=200, random_state=seed).fit(X_raw_tr, y_tr)
    mlp_exp = MLPClassifier(hidden_layer_sizes=(16, 8), max_iter=200, random_state=seed).fit(X_exp_tr, y_tr)

    class_models = [
        ("SVM (Raw)", svm_raw, X_raw_te),
        ("SVM (Legendre-Bessel)", svm_exp, X_exp_te),
        ("Random Forest (Raw)", rf_raw, X_raw_te),
        ("Random Forest (Legendre-Bessel)", rf_exp, X_exp_te),
        ("MLP (Raw)", mlp_raw, X_raw_te),
        ("MLP (Legendre-Bessel)", mlp_exp, X_exp_te)
    ]

    for name, clf, X_test_curr in class_models:
        preds = clf.predict(X_test_curr)
        probs = clf.predict_proba(X_test_curr)[:, 1]
        results[name]["acc"].append(accuracy_score(y_te, preds))
        results[name]["f1"].append(f1_score(y_te, preds, zero_division=0))
        results[name]["auc"].append(roc_auc_score(y_te, probs))

    # 4. Standard QNN (Raw)
    std_acc, std_f1, std_auc = train_eval_qnn(baseline_qnn_circuit, X_raw_tr, y_tr, X_raw_te, y_te)
    results["Standard QNN (Raw AngleEmbedding)"]["acc"].append(std_acc)
    results["Standard QNN (Raw AngleEmbedding)"]["f1"].append(std_f1)
    results["Standard QNN (Raw AngleEmbedding)"]["auc"].append(std_auc)

    # 5. Proposed QNN (Legendre-Bessel Expansion)
    prop_acc, prop_f1, prop_auc = train_eval_qnn(proposed_qnn_circuit, X_exp_tr, y_tr, X_exp_te, y_te)
    results["Proposed QNN (Legendre-Bessel + PQC)"]["acc"].append(prop_acc)
    results["Proposed QNN (Legendre-Bessel + PQC)"]["f1"].append(prop_f1)
    results["Proposed QNN (Legendre-Bessel + PQC)"]["auc"].append(prop_auc)

# ==========================================
# 5. GENERATE SUMMARY & LATEX TABLE
# ==========================================
summary_rows = []
for m in models:
    acc_mean, acc_std = np.mean(results[m]["acc"]) * 100, np.std(results[m]["acc"]) * 100
    f1_mean, f1_std = np.mean(results[m]["f1"]) * 100, np.std(results[m]["f1"]) * 100
    auc_mean, auc_std = np.mean(results[m]["auc"]), np.std(results[m]["auc"])
    
    summary_rows.append({
        "Model": m,
        "Accuracy (%)": f"{acc_mean:.2f} ± {acc_std:.2f}",
        "F1-Score (%)": f"{f1_mean:.2f} ± {f1_std:.2f}",
        "ROC-AUC": f"{auc_mean:.4f} ± {auc_std:.4f}"
    })

df_results = pd.DataFrame(summary_rows)

print("\n" + "=" * 70)
print("FINAL BENCHMARK COMPARISON (10 SEEDS MEAN ± STD)")
print("=" * 70)
print(df_results.to_string(index=False))

print("\n--- LATEX TABLE FORMAT FOR PAPER ---")
for idx, row in df_results.iterrows():
    print(f"{row['Model']} & {row['Accuracy (%)']} & {row['F1-Score (%)']} & {row['ROC-AUC']} \\\\")
