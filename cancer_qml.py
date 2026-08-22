import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

import pennylane as qml
from scipy.special import eval_legendre, jv
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split

# ==========================================
# 1. HYPERPARAMETERS & CONFIGURATION
# ==========================================
N_QUBITS = 4
N_RAW_FEATURES = 4
L_DEG = 2  # Legendre polynomial max degree (P1, P2)
B_ORD = 2  # Bessel function max order (J0, J1)
QNN_LAYERS = 2  # Number of variational entangling layers
EPOCHS = 30
BATCH_SIZE = 32
LEARNING_RATE = 0.05

MODEL_FILE = "quantum_cancer_model.pth"
SCALER_FILE = "data_scalers.pkl"

TOTAL_EXPANDED_FEATURES = N_RAW_FEATURES * (1 + L_DEG + B_ORD)  # 4 * 5 = 20 features

# ==========================================
# 2. DATA PROCESSING & TRANSFORMATIONS
# ==========================================
def apply_legendre_bessel_transform(X_scaled):
    X_out = []
    if X_scaled.ndim == 1:
        X_scaled = X_scaled.reshape(1, -1)
        
    for row in X_scaled:
        expanded_row = []
        for x in row:
            expanded_row.append(x)  # Original feature
            # Legendre Expansion
            for deg in range(1, L_DEG + 1):
                expanded_row.append(eval_legendre(deg, x))
            # Bessel Expansion
            for order in range(B_ORD):
                expanded_row.append(jv(order, x))
        X_out.append(expanded_row)
        
    return np.array(X_out)

def load_and_preprocess_data():
    print("Loading cancer dataset from scikit-learn...")
    data = load_breast_cancer()
    X_raw = data.data[:, :N_RAW_FEATURES]
    y_raw = data.target

    std_scaler = StandardScaler()
    minmax_scaler = MinMaxScaler(feature_range=(-1, 1))
    
    X_std = std_scaler.fit_transform(X_raw)
    X_scaled = minmax_scaler.fit_transform(X_std)

    with open(SCALER_FILE, "wb") as f:
        pickle.dump({"std_scaler": std_scaler, "minmax_scaler": minmax_scaler}, f)
    print(f"Scalers saved to {SCALER_FILE}")

    X_trans = apply_legendre_bessel_transform(X_scaled)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_trans, y_raw, test_size=0.2, random_state=42
    )

    X_train_t = torch.tensor(X_train, dtype=torch.float32, device='cpu')
    y_train_t = torch.tensor(y_train, dtype=torch.float32, device='cpu').unsqueeze(1)
    X_test_t = torch.tensor(X_test, dtype=torch.float32, device='cpu')
    y_test_t = torch.tensor(y_test, dtype=torch.float32, device='cpu').unsqueeze(1)
    
    return X_train_t, X_test_t, y_train_t, y_test_t, X_scaled, y_raw, data.feature_names[:N_RAW_FEATURES]

# ==========================================
# 3. PENNYLANE QUANTUM CIRCUIT
# ==========================================
dev = qml.device("default.qubit", wires=N_QUBITS)

@qml.qnode(dev, interface="torch")
def qnn_circuit(inputs, weights):
    cycles = TOTAL_EXPANDED_FEATURES // N_QUBITS
    
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

# ==========================================
# 4. PYTORCH HYBRID MODULE
# ==========================================
class QuantumClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        weight_shapes = {"weights": (QNN_LAYERS, N_QUBITS, 3)}
        self.qlayer = qml.qnn.TorchLayer(qnn_circuit, weight_shapes)
        self.fc = nn.Linear(1, 1)

    def forward(self, x):
        q_out = self.qlayer(x)
        if q_out.dim() == 1:
            q_out = q_out.unsqueeze(1)
        else:
            q_out = q_out.reshape(-1, 1)
        return torch.sigmoid(self.fc(q_out))

# ==========================================
# 5. TRAINING ROUTINE
# ==========================================
def train_and_save_model():
    X_train, X_test, y_train, y_test, X_scaled, y_raw, feature_names = load_and_preprocess_data()
    print(f"Data ready. Total features per sample: {X_train.shape[1]}")
    
    model = QuantumClassifier()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    loss_history = []
    acc_history = []

    print("\n--- TRAINING QUANTUM MODEL (CPU) ---")
    for epoch in range(EPOCHS):
        model.train()
        permutation = torch.randperm(X_train.size()[0])
        total_loss = 0.0

        for i in range(0, X_train.size()[0], BATCH_SIZE):
            indices = permutation[i : i + BATCH_SIZE]
            batch_x, batch_y = X_train[indices], y_train[indices]

            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        loss_history.append(total_loss)

        model.eval()
        with torch.no_grad():
            test_preds = model(X_test)
            binary_preds = (test_preds > 0.5).float()
            acc = (binary_preds == y_test).sum().item() / y_test.size(0)
            acc_history.append(acc)

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:02d}/{EPOCHS} | Train Loss: {total_loss:.4f} | Test Accuracy: {acc * 100:.2f}%")

    torch.save(model.state_dict(), MODEL_FILE)
    print(f"\nModel state dictionary saved to '{MODEL_FILE}'")
    
    return X_test, y_test, loss_history, acc_history, X_scaled, y_raw, feature_names

# ==========================================
# 6. INFERENCE & VISUALIZATION ROUTINE
# ==========================================
def predict_and_visualize(raw_sample, loss_hist, acc_hist, X_scaled, y_raw, feature_names):
    print("\n--- RUNNING INFERENCE & GENERATING PLOTS ---")
    
    with open(SCALER_FILE, "rb") as f:
        scalers = pickle.load(f)
    std_scaler = scalers["std_scaler"]
    minmax_scaler = scalers["minmax_scaler"]

    sample_arr = np.array(raw_sample).reshape(1, -1)
    sample_std = std_scaler.transform(sample_arr)
    sample_scaled = minmax_scaler.transform(sample_std)
    
    sample_trans = apply_legendre_bessel_transform(sample_scaled)
    sample_tensor = torch.tensor(sample_trans, dtype=torch.float32, device='cpu')

    loaded_model = QuantumClassifier()
    loaded_model.load_state_dict(torch.load(MODEL_FILE, map_location='cpu'))
    loaded_model.eval()

    with torch.no_grad():
        prob = loaded_model(sample_tensor).item()
        # SciKit-Learn label correction: 0 = Malignant, 1 = Benign
        malignant_prob = (1.0 - prob) * 100
        prediction = "Malignant (Cancerous)" if prob < 0.5 else "Benign (Non-Cancerous)"

    print(f"Raw Input Features: {raw_sample}")
    print(f"Calculated Malignancy Probability: {malignant_prob:.2f}%")
    print(f"Final Classification: {prediction}")

    # ----------------------------------------------------
    # MATPLOTLIB PLOT 1: Training Loss & Accuracy Dynamics
    # ----------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(8, 4))
    
    color = 'tab:red'
    ax1.set_xlabel('Epochs')
    ax1.set_ylabel('Loss', color=color)
    ax1.plot(loss_hist, color=color, linewidth=2, label='Training Loss')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Test Accuracy', color=color)
    ax2.plot(acc_hist, color=color, linewidth=2, linestyle='--', label='Test Accuracy')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Quantum Model Learning Curves (Legendre-Bessel Preprocessing)', fontweight='bold')
    fig.tight_layout()
    plt.show()

    # ----------------------------------------------------
    # MATPLOTLIB PLOT 2: Anatomical Breast Spatial Overlay
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 7))
    
    # Outer breast contour
    theta = np.linspace(0, 2 * np.pi, 200)
    r_outer = 5.0
    ax.plot(r_outer * np.cos(theta), r_outer * np.sin(theta), color='pink', linewidth=3)
    ax.fill(r_outer * np.cos(theta), r_outer * np.sin(theta), color='pink', alpha=0.15)

    # Areola & Nipple
    ax.add_patch(plt.Circle((0, 0), 0.8, color='crimson', alpha=0.3))
    ax.add_patch(plt.Circle((0, 0), 0.3, color='maroon'))

    # Quadrant lines
    ax.axhline(0, color='gray', linestyle='--', alpha=0.6)
    ax.axvline(0, color='gray', linestyle='--', alpha=0.6)

    ax.text(2.2, 2.2, 'Upper Outer (UO)', fontsize=9, fontweight='bold', ha='center')
    ax.text(-2.2, 2.2, 'Upper Inner (UI)', fontsize=9, fontweight='bold', ha='center')
    ax.text(2.2, -2.2, 'Lower Outer (LO)', fontsize=9, fontweight='bold', ha='center')
    ax.text(-2.2, -2.2, 'Lower Inner (LI)', fontsize=9, fontweight='bold', ha='center')

    # Plot sample tumor location (placed in UO quadrant with size proportional to radius)
    tumor_radius = (raw_sample[0] / 20.0) * 1.5  # Scale radius for visual display
    tumor_color = 'red' if prob < 0.5 else 'green'
    
    ax.add_patch(plt.Circle((2.5, 1.8), tumor_radius, color=tumor_color, alpha=0.6, edgecolor='black'))
    ax.plot(2.5, 1.8, 'k+', markersize=10)
    ax.text(2.5, 1.8 + tumor_radius + 0.3, f"Inferred Sample\n{prediction}\n({malignant_prob:.1f}% Malignant)", 
            fontsize=9, ha='center', fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1))

    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_aspect('equal')
    ax.set_title('Spatial Breast Mapping & Clinical Prediction Overlay', fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.4)
    plt.show()

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    X_test, y_test, loss_hist, acc_hist, X_scaled, y_raw, feature_names = train_and_save_model()
    
    # Sample biopsy values: [mean_radius, mean_texture, mean_perimeter, mean_area]
    sample_biopsy = [17.99, 10.38, 122.80, 1001.0] 
    predict_and_visualize(sample_biopsy, loss_hist, acc_hist, X_scaled, y_raw, feature_names)
