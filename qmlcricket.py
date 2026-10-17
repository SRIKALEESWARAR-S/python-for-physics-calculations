
# ============================================================
# LegendreQ-Cricket Live Lab | Single-cell Colab implementation
# Synthetic T20 + Legendre projection + classical ML + QML
# ============================================================

%pip -q install pennylane scikit-learn

import math, random, time, warnings
from collections import deque

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, clear_output

import torch
from torch import nn
import pennylane as qml

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, f1_score

# ---------------- Configuration ----------------
SEED = 42
WINDOW = 12
ORDER = 3
N_MATCHES = 70
TRAIN_OVERS = 8
N_QUBITS = 4
N_LAYERS = 2
Q_EPOCHS = 4
Q_TRAIN_MAX = 140
Q_TEST_MAX = 60
LIVE_OVERS = 20
DELAY_SECONDS = 0.25

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.set_num_threads(1)

OUTCOMES = ["DOT", "1", "2", "3", "4", "6", "WICKET"]
RUNS = {"DOT": 0, "1": 1, "2": 2, "3": 3, "4": 4, "6": 6, "WICKET": 0}

def softmax(x):
    x = np.asarray(x, dtype=float)
    e = np.exp(x - np.max(x))
    return e / e.sum()

# ---------------- Synthetic cricket generator ----------------
class SyntheticT20:
    def __init__(self, seed=SEED, max_overs=20):
        self.rng = np.random.default_rng(seed)
        self.max_balls = max_overs * 6
        self.ball = 0
        self.runs = 0
        self.wickets = 0
        self.recent = deque(maxlen=12)
        self.momentum = 0.0
        self.aggression = 0.52
        self.control = 0.55
        self.rows = []

    def state_features(self):
        recent_runs = [RUNS[o] for o in self.recent]
        recent_wkts = sum(o == "WICKET" for o in self.recent)
        n = max(1, self.ball)
        phase = self.ball / self.max_balls
        boundary_rate = sum(o in ("4", "6") for o in self.recent) / max(1, len(self.recent))
        dot_rate = sum(o == "DOT" for o in self.recent) / max(1, len(self.recent))
        recent_rate = sum(recent_runs) * 6 / max(1, len(recent_runs))

        return np.array([
            phase, self.runs / n, self.wickets / 10,
            (self.runs * 6 / n) / 12, boundary_rate, dot_rate,
            recent_rate / 12, self.momentum, self.aggression,
            self.control, recent_wkts / max(1, len(self.recent)),
            math.sin(2 * math.pi * phase)
        ], dtype=np.float32)

    def step(self):
        if self.ball >= self.max_balls or self.wickets >= 10:
            return None

        features = self.state_features()
        phase = self.ball / self.max_balls
        pressure = np.clip(0.30 + 0.65 * phase + 0.20 * self.wickets / 10, 0, 1.3)
        m, a, c = self.momentum, self.aggression, self.control

        logits = [
            0.80 + 0.35*c + 0.25*pressure - 0.20*a - 0.20*m,
            1.05 + 0.10*a + 0.10*c + 0.10*m,
            0.25 + 0.20*a + 0.15*m,
            -0.75 + 0.30*a + 0.15*m,
            -0.05 + 0.90*a - 0.30*c + 0.30*m,
            -0.65 + 1.05*a - 0.40*c + 0.45*m,
            -1.05 + 0.50*pressure + 0.35*a + 0.45*c - 0.25*m
        ]

        probs = softmax(logits)
        outcome = self.rng.choice(OUTCOMES, p=probs)
        runs = RUNS[outcome]

        self.ball += 1
        self.runs += runs
        if outcome == "WICKET":
            self.wickets += 1
        self.recent.append(outcome)

        signal = (runs / 6) - (1.2 if outcome == "WICKET" else 0) \
                 - (0.18 if outcome == "DOT" else 0)

        self.momentum = float(np.clip(
            0.72*m + 0.42*signal + self.rng.normal(0, 0.12), -1, 1
        ))
        self.aggression = float(np.clip(
            a + self.rng.normal(0, 0.035)
            + (0.015 if outcome in ("4", "6") else 0), 0.15, 0.95
        ))
        self.control = float(np.clip(
            c + self.rng.normal(0, 0.025)
            + (0.02 if outcome == "DOT" else -0.015 if outcome in ("4", "6") else 0),
            0.15, 0.95
        ))

        row = {
            "ball": self.ball,
            "over": f"{(self.ball-1)//6}.{(self.ball-1)%6+1}",
            "outcome": outcome,
            "runs_this_ball": runs,
            "total_runs": self.runs,
            "wickets": self.wickets,
            "run_rate": self.runs * 6 / self.ball,
            "momentum": self.momentum,
            "pressure": float(pressure),
            "features": features,
            "probabilities": probs
        }
        self.rows.append(row)
        return row

# ---------------- Legendre feature projection ----------------
def legendre_project(window, order=ORDER):
    window = np.asarray(window, dtype=np.float64)
    T, F = window.shape
    t = np.linspace(-1, 1, T)
    V = np.polynomial.legendre.legvander(t, order)
    result = []

    for j in range(F):
        s = window[:, j]
        s = (s - s.mean()) / (s.std() + 1e-6)
        coeff, *_ = np.linalg.lstsq(V, s, rcond=None)
        result.extend(coeff)

    return np.asarray(result, dtype=np.float32)

# ---------------- Build training dataset ----------------
print("Generating independent synthetic cricket innings...")
Xraw, Xleg, labels = [], [], []

for match_id in range(N_MATCHES):
    match = SyntheticT20(seed=1000 + match_id, max_overs=TRAIN_OVERS)
    while match.step() is not None:
        pass

    rows = match.rows
    for i in range(WINDOW, len(rows)):
        w = np.asarray(
            [r["features"] for r in rows[i-WINDOW:i]], dtype=np.float32
        )
        Xraw.append(w.flatten())
        Xleg.append(legendre_project(w))
        labels.append(OUTCOMES.index(rows[i]["outcome"]))

Xraw = np.asarray(Xraw, dtype=np.float32)
Xleg = np.asarray(Xleg, dtype=np.float32)
y = np.asarray(labels, dtype=np.int64)

if len(y) < 50 or len(np.unique(y)) < 2:
    raise RuntimeError("Insufficient training examples; increase N_MATCHES.")

print("Raw input shape:", Xraw.shape)
print("Legendre input shape:", Xleg.shape)
print("Outcome counts:", dict(zip(OUTCOMES, np.bincount(y, minlength=7))))

# ---------------- Split and scale ----------------
idx = np.arange(len(y))
itr, ite = train_test_split(
    idx, test_size=0.25, random_state=SEED, stratify=y
)

sc_raw, sc_leg = StandardScaler(), StandardScaler()
Xraw_tr = sc_raw.fit_transform(Xraw[itr]).astype(np.float32)
Xraw_te = sc_raw.transform(Xraw[ite]).astype(np.float32)
Xleg_tr = sc_leg.fit_transform(Xleg[itr]).astype(np.float32)
Xleg_te = sc_leg.transform(Xleg[ite]).astype(np.float32)

# ---------------- Classical MLP baselines ----------------
class MLPClassifier(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 64), nn.ReLU(), nn.Dropout(0.15),
            nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 7)
        )

    def forward(self, x):
        return self.net(x)

def train_mlp(Xtr, ytr, Xte, epochs=30):
    model = MLPClassifier(Xtr.shape[1]).float()
    opt = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss()

    xt = torch.tensor(Xtr, dtype=torch.float32)
    yt = torch.tensor(ytr, dtype=torch.long)

    for _ in range(epochs):
        model.train()
        opt.zero_grad()
        loss = loss_fn(model(xt), yt)
        loss.backward()
        opt.step()

    model.eval()
    with torch.no_grad():
        pred = model(torch.tensor(Xte, dtype=torch.float32)).argmax(1).numpy()
    return model, pred

print("\\nTraining classical baselines...")
mlp_raw, pred_raw = train_mlp(Xraw_tr, y[itr], Xraw_te)
mlp_leg, pred_leg = train_mlp(Xleg_tr, y[itr], Xleg_te)

# ---------------- Quantum model preparation ----------------
print("\\nPreparing 4-qubit variational classifier...")
pca = PCA(n_components=N_QUBITS, random_state=SEED)
Ztr = pca.fit_transform(Xleg_tr).astype(np.float32)
Zte = pca.transform(Xleg_te).astype(np.float32)

angle_scaler = StandardScaler()
Ztr = angle_scaler.fit_transform(Ztr).astype(np.float32)
Zte = angle_scaler.transform(Zte).astype(np.float32)
Ztr = (np.clip(Ztr, -2.5, 2.5) * (np.pi / 2.5)).astype(np.float32)
Zte = (np.clip(Zte, -2.5, 2.5) * (np.pi / 2.5)).astype(np.float32)

qdev = qml.device("default.qubit", wires=N_QUBITS)

@qml.qnode(qdev, interface="torch", diff_method="backprop")
def quantum_circuit(inputs, weights):
    for i in range(N_QUBITS):
        qml.RY(inputs[i], wires=i)

    for layer in range(N_LAYERS):
        for i in range(N_QUBITS):
            qml.RY(weights[layer, i, 0], wires=i)
            qml.RZ(weights[layer, i, 1], wires=i)
        for i in range(N_QUBITS - 1):
            qml.CNOT(wires=[i, i+1])
        qml.CNOT(wires=[N_QUBITS-1, 0])

    return [qml.expval(qml.PauliZ(i)) for i in range(N_QUBITS)]

class LegendreQClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.qweights = nn.Parameter(
            0.05 * torch.randn(N_LAYERS, N_QUBITS, 2, dtype=torch.float32)
        )
        self.head = nn.Linear(N_QUBITS, len(OUTCOMES)).float()

    def forward(self, x):
        x = x.to(dtype=torch.float32)
        qout = torch.stack([
            torch.stack(quantum_circuit(row, self.qweights))
            for row in x
        ]).to(dtype=torch.float32)
        return self.head(qout)

rng = np.random.default_rng(SEED)
qtr_idx = rng.choice(len(Ztr), min(Q_TRAIN_MAX, len(Ztr)), replace=False)
qte_idx = rng.choice(len(Zte), min(Q_TEST_MAX, len(Zte)), replace=False)

Zqtr = torch.tensor(Ztr[qtr_idx], dtype=torch.float32)
yqtr = torch.tensor(y[itr][qtr_idx], dtype=torch.long)
Zqte = torch.tensor(Zte[qte_idx], dtype=torch.float32)
yqte = y[ite][qte_idx]

qmodel = LegendreQClassifier().float()
qopt = torch.optim.Adam(qmodel.parameters(), lr=0.025)
qloss = nn.CrossEntropyLoss()
qhistory = []

print("Training QML model; this may take a few minutes on CPU...")
for epoch in range(Q_EPOCHS):
    qmodel.train()
    qopt.zero_grad()
    logits = qmodel(Zqtr)
    loss = qloss(logits, yqtr)
    loss.backward()
    qopt.step()
    qhistory.append(float(loss.detach()))
    print(f"Epoch {epoch+1}/{Q_EPOCHS} | loss={qhistory[-1]:.4f}")

qmodel.eval()
with torch.no_grad():
    pred_q = qmodel(Zqte).argmax(1).cpu().numpy()

# ---------------- Benchmark ----------------
results = pd.DataFrame([
    {"Model": "Raw-window MLP",
     "Accuracy": accuracy_score(y[ite], pred_raw),
     "Macro-F1": f1_score(y[ite], pred_raw, average="macro", zero_division=0)},
    {"Model": "Legendre-window MLP",
     "Accuracy": accuracy_score(y[ite], pred_leg),
     "Macro-F1": f1_score(y[ite], pred_leg, average="macro", zero_division=0)},
    {"Model": "Legendre-QML (subset)",
     "Accuracy": accuracy_score(yqte, pred_q),
     "Macro-F1": f1_score(yqte, pred_q, average="macro", zero_division=0)}
])
print("\\nSYNTHETIC HELD-OUT BENCHMARK — NOT REAL-CRICKET PERFORMANCE")
display(results)

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.bar(results["Model"], results["Accuracy"])
ax.set_ylim(0, 1)
ax.set_ylabel("Accuracy")
ax.set_title("Synthetic cricket benchmark")
ax.tick_params(axis="x", rotation=12)
ax.grid(axis="y", alpha=0.25)
plt.show()

# ---------------- Live dashboard ----------------
def state_window_from_match(match):
    feats = [r["features"] for r in match.rows]
    if not feats:
        return np.zeros((WINDOW, 12), dtype=np.float32)
    arr = np.asarray(feats[-WINDOW:], dtype=np.float32)
    if len(arr) < WINDOW:
        arr = np.vstack([np.repeat(arr[:1], WINDOW-len(arr), axis=0), arr])
    return arr

def qml_predict_next(match):
    w = state_window_from_match(match)
    leg = legendre_project(w).reshape(1, -1)
    leg_scaled = sc_leg.transform(leg).astype(np.float32)
    z = pca.transform(leg_scaled).astype(np.float32)
    z = angle_scaler.transform(z).astype(np.float32)
    z = (np.clip(z, -2.5, 2.5) * (np.pi/2.5)).astype(np.float32)

    with torch.no_grad():
        logits = qmodel(torch.tensor(z, dtype=torch.float32))
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
    return probs

def draw_dashboard(match, latest=None):
    rows = match.rows
    clear_output(wait=True)

    fig = plt.figure(figsize=(14, 8), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, height_ratios=[0.8, 1.5, 1.2])
    ax_score = fig.add_subplot(gs[0, :])
    ax_balls = fig.add_subplot(gs[1, 0])
    ax_scoreline = fig.add_subplot(gs[1, 1])
    ax_dynamics = fig.add_subplot(gs[2, 0])
    ax_probs = fig.add_subplot(gs[2, 1])

    n = len(rows)
    overs = f"{n//6}.{n%6}"
    crr = match.runs * 6 / max(1, n)

    ax_score.axis("off")
    ax_score.text(0.01, 0.77, "LEGENDREQ-CRICKET LIVE LAB",
                  fontsize=16, weight="bold", transform=ax_score.transAxes)
    ax_score.text(0.01, 0.30,
                  f"SCORE  {match.runs}/{match.wickets}     OVERS  {overs}     CRR  {crr:.2f}",
                  fontsize=17, transform=ax_score.transAxes)
    event = f"Latest: {latest['over']} — {latest['outcome']}" if latest else "Starting"
    ax_score.text(0.70, 0.30, event, fontsize=13, weight="bold",
                  transform=ax_score.transAxes)

    recent = rows[-24:]
    if recent:
        vals = [r["runs_this_ball"] for r in recent]
        colors = [
            "crimson" if r["outcome"] == "WICKET"
            else "darkorange" if r["outcome"] in ("4", "6")
            else "steelblue" for r in recent
        ]
        ax_balls.bar(range(len(vals)), vals, color=colors)
        ax_balls.set_xticks(range(len(vals)))
        ax_balls.set_xticklabels([r["over"] for r in recent], rotation=60, fontsize=7)
    ax_balls.set_title("Recent ball-by-ball runs")
    ax_balls.set_ylabel("Runs"); ax_balls.grid(axis="y", alpha=0.2)

    if rows:
        x = np.arange(1, n+1)
        ax_scoreline.plot(x, [r["total_runs"] for r in rows], label="Total runs")
        ax_scoreline.set_xlabel("Ball"); ax_scoreline.set_ylabel("Runs")
        ax_scoreline.set_title("Innings trajectory")
        ax_scoreline.grid(alpha=0.25)
        ax2 = ax_scoreline.twinx()
        ax2.plot(x, [r["run_rate"] for r in rows], "--", label="Run rate")
        ax2.set_ylabel("Run rate")
        h1, l1 = ax_scoreline.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax_scoreline.legend(h1+h2, l1+l2, fontsize=8)

        ax_dynamics.plot(x, [r["momentum"] for r in rows], label="Momentum")
        ax_dynamics.plot(x, [r["pressure"] for r in rows], label="Pressure")
    ax_dynamics.set_title("Synthetic latent dynamics")
    ax_dynamics.set_xlabel("Ball"); ax_dynamics.legend(fontsize=8)
    ax_dynamics.grid(alpha=0.25)

    if rows:
        probs = qml_predict_next(match)
        ax_probs.bar(OUTCOMES, probs)
        ax_probs.set_ylim(0, 1)
        ax_probs.set_title("QML next-outcome scores (synthetic)")
        ax_probs.tick_params(axis="x", rotation=25)
        ax_probs.set_ylabel("Softmax score")
    else:
        ax_probs.set_title("QML next-outcome scores")

    plt.show()
    plt.close(fig)
    time.sleep(DELAY_SECONDS)

print("\\nStarting live synthetic T20 simulation...")
live_match = SyntheticT20(seed=2026, max_overs=LIVE_OVERS)

for _ in range(live_match.max_balls):
    delivery = live_match.step()
    if delivery is None:
        break
    draw_dashboard(live_match, latest=delivery)

print(f"INNINGS COMPLETE: {live_match.runs}/{live_match.wickets} "
      f"in {len(live_match.rows)//6}.{len(live_match.rows)%6} overs")

# ---------------- Export ----------------
export_rows = [
    {k: v for k, v in r.items() if k not in ("features", "probabilities")}
    for r in live_match.rows
]
live_df = pd.DataFrame(export_rows)
csv_path = "/content/legendreq_cricket_synthetic_match.csv"
live_df.to_csv(csv_path, index=False)
print("Synthetic ball-by-ball CSV saved to:", csv_path)
display(live_df.head(12))

