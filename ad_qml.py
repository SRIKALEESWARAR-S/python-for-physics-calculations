import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import pennylane as qml
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from scipy.special import eval_legendre, jv
from sklearn.datasets import load_breast_cancer, load_diabetes
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

# ==========================================
# 1. CONFIGURATION & MATH TRANSFORMATIONS
# ==========================================
L_DEG = 2  # Legendre polynomial max degree (P1, P2)
B_ORD = 2  # Bessel function max order (J0, J1)
EXPANSION_FACTOR = 1 + L_DEG + B_ORD  # Total multiplier per feature (5)

def functional_expansion(X_scaled):
    """Projects features into higher-dimensional Legendre-Bessel space."""
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

def prepare_clinical_dataset(dataset_name, target_qubits=8):
    """Loads, standardizes, applies PCA, and performs functional expansion."""
    if dataset_name == "Breast Cancer (30 Features)":
        data = load_breast_cancer()
        X, y = data.data, 1 - data.target  # 1 = Malignant, 0 = Benign
    elif dataset_name == "Diabetes Risk (10 Features)":
        data = load_diabetes()
        X = data.data
        y = (data.target > np.median(data.target)).astype(int)  # Binary risk threshold

    std_scaler = StandardScaler()
    pca = PCA(n_components=target_qubits)
    minmax = MinMaxScaler(feature_range=(-1, 1))
    
    X_pca = pca.fit_transform(std_scaler.fit_transform(X))
    X_norm = minmax.fit_transform(X_pca)
    
    X_expanded = functional_expansion(X_norm)
    
    return train_test_split(X_expanded, y, test_size=0.2, random_state=42, stratify=y), X_norm, X_expanded, y

# ==========================================
# 2. SCALABLE QUANTUM ARCHITECTURE
# ==========================================
def build_scalable_qnode(n_qubits, layers=2):
    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev, interface="torch")
    def circuit(inputs, weights):
        total_features = inputs.shape[-1]
        cycles = int(np.ceil(total_features / n_qubits))

        # Data Re-uploading Loop across rotation axes
        for c in range(cycles):
            start = c * n_qubits
            end = min((c + 1) * n_qubits, total_features)
            slice_len = end - start
            
            feat_slice = inputs[..., start:end]
            axis = 'X' if c % 3 == 0 else ('Y' if c % 3 == 1 else 'Z')
            qml.AngleEmbedding(feat_slice, wires=range(slice_len), rotation=axis)

        # Strongly Entangling Layers
        for L in range(layers):
            for q in range(n_qubits):
                qml.Rot(weights[L, q, 0], weights[L, q, 1], weights[L, q, 2], wires=q)
            for q in range(n_qubits):
                qml.CNOT(wires=[q, (q + 1) % n_qubits])

        return qml.expval(qml.PauliZ(0))
    return circuit

class ClinicalHybridQNN(nn.Module):
    def __init__(self, n_qubits=8, layers=2):
        super().__init__()
        self.circuit_fn = build_scalable_qnode(n_qubits, layers)
        weight_shapes = {"weights": (layers, n_qubits, 3)}
        self.qlayer = qml.qnn.TorchLayer(self.circuit_fn, weight_shapes)
        self.fc = nn.Linear(1, 1)

    def forward(self, x):
        return torch.sigmoid(self.fc(self.qlayer(x).reshape(-1, 1)))

# ==========================================
# 3. TRAINING ENGINE
# ==========================================
def train_model(dataset_name, n_qubits=8, epochs=15):
    splits, X_pca, X_expanded, labels = prepare_clinical_dataset(dataset_name, n_qubits)
    X_tr, X_te, y_tr, y_te = splits
    
    X_tr_t = torch.tensor(X_tr, dtype=torch.float32)
    y_tr_t = torch.tensor(y_tr, dtype=torch.float32).unsqueeze(1)
    X_te_t = torch.tensor(X_te, dtype=torch.float32)

    model = ClinicalHybridQNN(n_qubits=n_qubits)
    opt = optim.Adam(model.parameters(), lr=0.05)
    loss_fn = nn.BCELoss()

    loss_history, auc_history = [], []

    print(f"\nTraining on: {dataset_name} | Qubits: {n_qubits} | Expanded Features: {X_tr.shape[1]}")
    
    for epoch in range(epochs):
        model.train()
        opt.zero_grad()
        loss = loss_fn(model(X_tr_t), y_tr_t)
        loss.backward()
        opt.step()
        
        loss_history.append(loss.item())
        
        model.eval()
        with torch.no_grad():
            preds = model(X_te_t).numpy().flatten()
            auc = roc_auc_score(y_te, preds)
            auc_history.append(auc)

    return model, loss_history, auc_history, X_pca, X_expanded, labels

# ==========================================
# 4. ADVANCED VISUALIZATION SUITE
# ==========================================
def run_experiments_and_plot():
    target_q = 8
    datasets = ["Breast Cancer (30 Features)", "Diabetes Risk (10 Features)"]
    results = {}

    for ds in datasets:
        model, losses, aucs, X_pca, X_exp, y_raw = train_model(ds, n_qubits=target_q, epochs=15)
        results[ds] = {"losses": losses, "aucs": aucs, "X_pca": X_pca, "X_exp": X_exp, "y": y_raw, "model": model}

    fig = plt.figure(figsize=(18, 10))
    gs = GridSpec(2, 3, figure=fig)
    plt.suptitle("Quantum Clinical Multi-Dataset Validation Suite", fontsize=18, fontweight='bold')

    bc_data = results["Breast Cancer (30 Features)"]

    # --- PLOT 1: Standard Linear PCA Space ---
    ax_pca = fig.add_subplot(gs[0, 0], projection='3d')
    ax_pca.scatter(bc_data["X_pca"][:, 0], bc_data["X_pca"][:, 1], bc_data["X_pca"][:, 2], 
                   c=bc_data["y"], cmap='coolwarm', alpha=0.7, edgecolor='k')
    ax_pca.set_title("Standard Linear PCA Space", fontweight='bold')
    ax_pca.set_xlabel("PC 1"); ax_pca.set_ylabel("PC 2"); ax_pca.set_zlabel("PC 3")

    # --- PLOT 2: True Legendre-Bessel Non-Linear Manifold ---
    # Indices 2, 3, 4 represent higher-order terms: P2(x0), J0(x1), and J1(x2)
    ax_exp = fig.add_subplot(gs[0, 1], projection='3d')
    ax_exp.scatter(bc_data["X_exp"][:, 2], bc_data["X_exp"][:, 3], bc_data["X_exp"][:, 4], 
                   c=bc_data["y"], cmap='coolwarm', alpha=0.7, edgecolor='k')
    ax_exp.set_title("Legendre-Bessel Transformed Space", fontweight='bold')
    ax_exp.set_xlabel(r"$P_2(x_0)$ (Legendre)"); ax_exp.set_ylabel(r"$J_0(x_1)$ (Bessel)"); ax_exp.set_zlabel(r"$J_1(x_2)$ (Bessel)")

    # --- PLOT 3: Scaled Quantum Circuit Diagram ---
    ax_circ = fig.add_subplot(gs[0, 2])
    dummy_input = torch.rand(1, target_q * EXPANSION_FACTOR)
    dummy_weights = torch.rand(2, target_q, 3)
    
    fig_circ, ax_c = qml.draw_mpl(results["Breast Cancer (30 Features)"]["model"].circuit_fn, decimals=2)(dummy_input, dummy_weights)
    fig_circ.canvas.draw()
    
    ax_circ.imshow(fig_circ.canvas.renderer.buffer_rgba())
    ax_circ.axis('off')
    ax_circ.set_title(f"Dynamic {target_q}-Qubit PQC Topology", fontweight='bold')
    plt.close(fig_circ)

    # --- PLOTS 4 & 5: Comparative Learning Curves ---
    colors = ['tab:blue', 'tab:orange']
    
    ax_loss = fig.add_subplot(gs[1, :2])
    ax_auc = fig.add_subplot(gs[1, 2])

    for idx, ds in enumerate(datasets):
        ax_loss.plot(results[ds]["losses"], label=ds, color=colors[idx], linewidth=2.5, marker='o')
        ax_auc.plot(results[ds]["aucs"], label=ds, color=colors[idx], linewidth=2.5, linestyle='--')

    ax_loss.set_title("Training Loss Convergence across Datasets", fontweight='bold')
    ax_loss.set_ylabel("BCE Loss"); ax_loss.set_xlabel("Epochs")
    ax_loss.legend()
    ax_loss.grid(True, alpha=0.3)

    ax_auc.set_title("Validation ROC-AUC", fontweight='bold')
    ax_auc.set_ylabel("AUC Score"); ax_auc.set_xlabel("Epochs")
    ax_auc.legend()
    ax_auc.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_experiments_and_plot()
