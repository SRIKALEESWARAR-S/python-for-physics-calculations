"""
Headless Hybrid QML Benchmark
=============================

Hybrid QML:
    LSTM -> Ry angle encoding -> inverse QFT -> variational ansatz -> linear head

Baselines:
    1. Classical LSTM
    2. Classical MLP

Features:
    - Correct batched processing of quantum layer
    - No GUI
    - No hardware dependency
    - Progress bars
    - Loss
    - Accuracy
    - Wall-clock latency
    - Peak memory
    - Parameter counts
"""

import argparse
import csv
import math
import os
import time
import tracemalloc

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn

try:
    from tqdm import tqdm
except ImportError:
    raise SystemExit(
        "tqdm is not installed.\n"
        "Install it with:\n"
        "    python -m pip install tqdm"
    )

try:
    import pennylane as qml
    HAVE_PENNYLANE = True
except ImportError:
    HAVE_PENNYLANE = False


# ============================================================
# 1. Reproducibility
# ============================================================

torch.set_default_dtype(torch.float32)


# ============================================================
# 2. Higher-order nonlinear synthetic signal generator
# ============================================================

class NonlinearOpticalSimulator:
    """
    Generates a 3-channel nonlinear RGB optical signal.

    Components:
      - quasi-periodic sinusoidal components
      - chaotic logistic-map driver
      - nonlinear cross-channel coupling
      - additive sensor noise
    """

    def __init__(self, dt=0.05, noise_std=0.02, seed=0):
        self.dt = dt
        self.noise_std = noise_std
        self.rng = np.random.default_rng(seed)

        self.t = 0.0
        self.chaos = 0.42

    def _logistic_step(self):
        self.chaos = 3.97 * self.chaos * (1.0 - self.chaos)
        return self.chaos

    def step(self):
        t = self.t
        c = self._logistic_step()

        r = (
            0.5
            + 0.22 * math.sin(0.9 * t)
            + 0.12 * math.sin(2.7 * t) * c
        )

        g = (
            0.5
            + 0.20 * math.cos(0.6 * t + 0.4)
            + 0.15 * (r ** 2 - 0.25)
        )

        b = (
            0.5
            + 0.18 * math.sin(0.35 * t) * math.cos(1.3 * t)
            + 0.10 * (c ** 2)
        )

        coupling = (
            0.08
            * math.sin(r * g * 6.0)
            * math.cos(b * 4.0)
        )

        r += coupling
        g -= 0.5 * coupling
        b += 0.3 * coupling

        r += self.rng.normal(0, self.noise_std)
        g += self.rng.normal(0, self.noise_std)
        b += self.rng.normal(0, self.noise_std)

        r = float(np.clip(r, 0.0, 1.0))
        g = float(np.clip(g, 0.0, 1.0))
        b = float(np.clip(b, 0.0, 1.0))

        self.t += self.dt

        return r, g, b

    def generate(self, n):
        return np.array(
            [self.step() for _ in range(n)],
            dtype=np.float32
        )


# ============================================================
# 3. Dataset
# ============================================================

def build_dataset(
    n_samples,
    window,
    horizon,
    dt=0.05,
    noise_std=0.02,
    seed=0,
):
    """
    X[i]:
        Past RGB window.

    y[i]:
        Future Sell/Hold/Buy state.

    The target is taken horizon steps after the input window,
    preventing same-timestep leakage.
    """

    sim = NonlinearOpticalSimulator(
        dt=dt,
        noise_std=noise_std,
        seed=seed,
    )

    raw = sim.generate(
        n_samples + window + horizon
    )

    X = []
    y = []

    for i in range(n_samples):

        window_slice = raw[i:i + window]

        future_point = raw[
            i + window + horizon - 1
        ]

        r_f, g_f, b_f = future_point

        ratio = b_f / (r_f + 1e-6)

        if ratio > 1.4:
            label = 2       # Buy

        elif ratio >= 0.8:
            label = 1       # Hold

        else:
            label = 0       # Sell

        X.append(window_slice)
        y.append(label)

    X = np.stack(X)
    y = np.array(y, dtype=np.int64)

    return X, y


# ============================================================
# 4. Quantum circuit
# ============================================================

N_QUBITS = 4
N_LAYERS = 3


if HAVE_PENNYLANE:

    dev = qml.device(
        "default.qubit",
        wires=N_QUBITS
    )

    def variational_ansatz(weights, wires):

        for l in range(weights.shape[0]):

            for i, w in enumerate(wires):

                qml.RZ(
                    weights[l, i, 0],
                    wires=w
                )

                qml.RY(
                    weights[l, i, 1],
                    wires=w
                )

                qml.RZ(
                    weights[l, i, 2],
                    wires=w
                )

            # Ring of CNOT gates
            for i in range(len(wires)):

                qml.CNOT(
                    wires=[
                        wires[i],
                        wires[(i + 1) % len(wires)]
                    ]
                )


    def make_qnode(diff_method="parameter-shift"):

        @qml.qnode(
            dev,
            interface="torch",
            diff_method=diff_method
        )
        def rgb_iqft_qnode(inputs, weights):

            wires = list(range(N_QUBITS))

            # ------------------------------------------------
            # Angle encoding
            # ------------------------------------------------

            qml.RY(
                inputs[0],
                wires=0
            )

            qml.RY(
                inputs[1],
                wires=1
            )

            # FIXED TYPO:
            # inputs, not inpuats
            qml.RY(
                inputs[2],
                wires=2
            )

            qml.RY(
                (inputs[0] + inputs[1] + inputs[2]) / 3.0,
                wires=3
            )

            # ------------------------------------------------
            # Inverse QFT
            # ------------------------------------------------

            qml.adjoint(
                qml.QFT
            )(wires=wires)

            # ------------------------------------------------
            # Variational circuit
            # ------------------------------------------------

            variational_ansatz(
                weights,
                wires
            )

            # ------------------------------------------------
            # Measurements
            # ------------------------------------------------

            return (
                qml.expval(
                    qml.PauliZ(0)
                    @ qml.PauliZ(1)
                ),

                *[
                    qml.expval(
                        qml.PauliZ(w)
                    )
                    for w in wires
                ],
            )

        # FIXED:
        # return the actual qnode
        return rgb_iqft_qnode


# ============================================================
# 5. Hybrid QML model
# ============================================================

class HybridQMLModel(nn.Module):

    def __init__(
        self,
        qnode,
        lstm_hidden=16
    ):

        super().__init__()

        self.qnode = qnode

        self.lstm = nn.LSTM(
            input_size=3,
            hidden_size=lstm_hidden,
            batch_first=True
        )

        self.to_angles = nn.Sequential(
            nn.Linear(lstm_hidden, 3),
            nn.Tanh()
        )

        self.q_weights = nn.Parameter(
            0.1 * torch.randn(
                N_LAYERS,
                N_QUBITS,
                3
            )
        )

        self.output_head = nn.Linear(
            N_QUBITS + 1,
            3
        )


    def forward(self, x):

        # ----------------------------------------------------
        # Classical LSTM feature extraction
        # ----------------------------------------------------

        _, (h_n, _) = self.lstm(x)

        angles = self.to_angles(
            h_n[-1]
        ) * math.pi

        # angles shape:
        # (batch, 3)

        outs = []

        # ----------------------------------------------------
        # IMPORTANT:
        # Process each sample independently.
        #
        # This avoids the old TorchLayer batching problem.
        # ----------------------------------------------------

        for i in range(angles.shape[0]):

            result = self.qnode(
                angles[i],
                self.q_weights
            )

            flat_result = torch.stack(
                [
                    r.reshape(())
                    for r in result
                ]
            )

            outs.append(flat_result)

        q_feat = torch.stack(
            outs,
            dim=0
        )

        q_feat = q_feat.float()

        return self.output_head(q_feat)


    def quantum_param_count(self):
        return self.q_weights.numel()


# ============================================================
# 6. Classical LSTM baseline
# ============================================================

class ClassicalLSTMBaseline(nn.Module):

    def __init__(
        self,
        hidden_size=64
    ):

        super().__init__()

        self.lstm = nn.LSTM(
            input_size=3,
            hidden_size=hidden_size,
            batch_first=True
        )

        self.head = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Linear(64, 3)
        )


    def forward(self, x):

        _, (h_n, _) = self.lstm(x)

        return self.head(
            h_n[-1]
        )


# ============================================================
# 7. Classical MLP baseline
# ============================================================

class ClassicalMLPBaseline(nn.Module):

    def __init__(
        self,
        window,
        hidden=64
    ):

        super().__init__()

        self.net = nn.Sequential(

            nn.Flatten(),

            nn.Linear(
                window * 3,
                hidden
            ),

            nn.ReLU(),

            nn.Linear(
                hidden,
                hidden
            ),

            nn.ReLU(),

            nn.Linear(
                hidden,
                3
            )
        )


    def forward(self, x):

        return self.net(x)


# ============================================================
# 8. Parameter counting
# ============================================================

def count_params(model):

    return sum(
        p.numel()
        for p in model.parameters()
        if p.requires_grad
    )


# ============================================================
# 9. Training
# ============================================================

def train_and_log(
    name,
    model,
    X_train,
    y_train,
    X_test,
    y_test,
    epochs,
    batch_size,
    lr,
    out_dir
):

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=lr
    )

    criterion = nn.CrossEntropyLoss()

    n_train = X_train.shape[0]

    # FIX:
    # Don't silently discard the final batch.
    steps_per_epoch = math.ceil(
        n_train / batch_size
    )

    log_path = os.path.join(
        out_dir,
        f"metrics_{name}.csv"
    )

    log_rows = []

    step_times = []

    peak_mem_bytes = 0

    tracemalloc.start()

    global_step = 0

    test_loss = None
    test_acc = None

    # ========================================================
    # Epoch loop
    # ========================================================

    epoch_bar = tqdm(
        range(epochs),
        desc=f"{name}",
        unit="epoch"
    )

    for epoch in epoch_bar:

        model.train()

        perm = np.random.permutation(
            n_train
        )

        # ----------------------------------------------------
        # Batch progress bar
        # ----------------------------------------------------

        batch_bar = tqdm(
            range(steps_per_epoch),
            desc=f"Epoch {epoch + 1}/{epochs}",
            unit="batch",
            leave=False
        )

        for b in batch_bar:

            start = b * batch_size
            end = min(
                start + batch_size,
                n_train
            )

            idx = perm[start:end]

            xb = torch.tensor(
                X_train[idx],
                dtype=torch.float32
            )

            yb = torch.tensor(
                y_train[idx],
                dtype=torch.long
            )

            t0 = time.perf_counter()

            optimizer.zero_grad(
                set_to_none=True
            )

            logits = model(xb)

            loss = criterion(
                logits,
                yb
            )

            loss.backward()

            optimizer.step()

            t1 = time.perf_counter()

            step_time = t1 - t0

            step_times.append(
                step_time
            )

            current, peak = (
                tracemalloc.get_traced_memory()
            )

            peak_mem_bytes = max(
                peak_mem_bytes,
                peak
            )

            train_acc = (
                logits.argmax(dim=1)
                == yb
            ).float().mean().item()

            global_step += 1

            log_rows.append(
                {
                    "step": global_step,
                    "epoch": epoch,
                    "loss": loss.item(),
                    "train_acc": train_acc,
                    "step_time_s": step_time,
                }
            )

            # Update progress bar
            batch_bar.set_postfix(
                loss=f"{loss.item():.4f}",
                acc=f"{train_acc:.3f}",
                ms=f"{step_time * 1000:.1f}"
            )

        batch_bar.close()

        # ====================================================
        # Test evaluation
        # ====================================================

        model.eval()

        with torch.no_grad():

            xt = torch.tensor(
                X_test,
                dtype=torch.float32
            )

            yt = torch.tensor(
                y_test,
                dtype=torch.long
            )

            eval_start = time.perf_counter()

            test_logits = model(xt)

            eval_time = (
                time.perf_counter()
                - eval_start
            )

            test_loss = criterion(
                test_logits,
                yt
            ).item()

            test_acc = (
                test_logits.argmax(dim=1)
                == yt
            ).float().mean().item()

        model.train()

        epoch_bar.set_postfix(
            test_loss=f"{test_loss:.4f}",
            test_acc=f"{test_acc:.3f}",
            eval_s=f"{eval_time:.1f}"
        )

        print(
            f"\n[{name}] "
            f"Epoch {epoch + 1}/{epochs} | "
            f"Test Loss: {test_loss:.4f} | "
            f"Test Acc: {test_acc:.3f}"
        )

    epoch_bar.close()

    tracemalloc.stop()

    # ========================================================
    # Save step logs
    # ========================================================

    with open(
        log_path,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "step",
                "epoch",
                "loss",
                "train_acc",
                "step_time_s"
            ]
        )

        writer.writeheader()

        writer.writerows(
            log_rows
        )

    # ========================================================
    # Summary
    # ========================================================

    quantum_params = (
        model.quantum_param_count()
        if hasattr(
            model,
            "quantum_param_count"
        )
        else None
    )

    summary = {

        "model": name,

        "total_trainable_params":
            count_params(model),

        "quantum_only_params":
            quantum_params
            if quantum_params is not None
            else "",

        "final_test_loss":
            test_loss,

        "final_test_acc":
            test_acc,

        "avg_step_time_ms":
            1000 * float(
                np.mean(step_times)
            ),

        "peak_memory_kb":
            peak_mem_bytes / 1024.0,
    }

    return log_rows, summary


# ============================================================
# 10. Plotting
# ============================================================

def plot_curves(
    all_logs,
    out_dir
):

    # --------------------------------------------------------
    # Loss
    # --------------------------------------------------------

    plt.figure(
        figsize=(9, 5)
    )

    for name, rows in all_logs.items():

        steps = [
            r["step"]
            for r in rows
        ]

        losses = [
            r["loss"]
            for r in rows
        ]

        plt.plot(
            steps,
            losses,
            label=name,
            alpha=0.85
        )

    plt.xlabel(
        "training step"
    )

    plt.ylabel(
        "loss"
    )

    plt.title(
        "Training loss: Hybrid QML vs classical baselines"
    )

    plt.legend()

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            out_dir,
            "loss_curves.png"
        ),
        dpi=150
    )

    plt.close()

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    plt.figure(
        figsize=(9, 5)
    )

    for name, rows in all_logs.items():

        steps = [
            r["step"]
            for r in rows
        ]

        accs = [
            r["train_acc"]
            for r in rows
        ]

        window = 10

        if len(accs) >= window:

            accs_smooth = np.convolve(
                accs,
                np.ones(window) / window,
                mode="valid"
            )

            plt.plot(
                steps[:len(accs_smooth)],
                accs_smooth,
                label=name,
                alpha=0.85
            )

        else:

            plt.plot(
                steps,
                accs,
                label=name,
                alpha=0.85
            )

    plt.xlabel(
        "training step"
    )

    plt.ylabel(
        "train accuracy (smoothed)"
    )

    plt.title(
        "Training accuracy: Hybrid QML vs classical baselines"
    )

    plt.legend()

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            out_dir,
            "accuracy_curves.png"
        ),
        dpi=150
    )

    plt.close()


# ============================================================
# 11. Latency vs parameters
# ============================================================

def plot_latency_vs_params(
    summaries,
    out_dir
):

    plt.figure(
        figsize=(7, 5)
    )

    for s in summaries:

        plt.scatter(
            s["total_trainable_params"],
            s["avg_step_time_ms"],
            s=120
        )

        plt.annotate(
            s["model"],
            (
                s["total_trainable_params"],
                s["avg_step_time_ms"]
            ),
            textcoords="offset points",
            xytext=(6, 6)
        )

    plt.xlabel(
        "total trainable parameters"
    )

    plt.ylabel(
        "avg step time (ms)"
    )

    plt.title(
        "Parameter budget vs. per-step latency"
    )

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            out_dir,
            "latency_vs_params.png"
        ),
        dpi=150
    )

    plt.close()


# ============================================================
# 12. Summary table
# ============================================================

def write_summary_table(
    summaries,
    out_dir
):

    csv_path = os.path.join(
        out_dir,
        "summary_table.csv"
    )

    md_path = os.path.join(
        out_dir,
        "summary_table.md"
    )

    fields = [
        "model",
        "total_trainable_params",
        "quantum_only_params",
        "final_test_loss",
        "final_test_acc",
        "avg_step_time_ms",
        "peak_memory_kb",
    ]

    with open(
        csv_path,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()

        writer.writerows(
            summaries
        )

    with open(
        md_path,
        "w"
    ) as f:

        f.write(
            "| Model | Total Params | Quantum-only Params | "
            "Test Loss | Test Acc | Avg Step (ms) | Peak Mem (KB) |\n"
        )

        f.write(
            "|---|---|---|---|---|---|---|\n"
        )

        for s in summaries:

            f.write(
                f"| {s['model']} | "
                f"{s['total_trainable_params']} | "
                f"{s['quantum_only_params']} | "
                f"{s['final_test_loss']:.4f} | "
                f"{s['final_test_acc']:.3f} | "
                f"{s['avg_step_time_ms']:.2f} | "
                f"{s['peak_memory_kb']:.1f} |\n"
            )

    return csv_path, md_path


# ============================================================
# 13. Main
# ============================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--samples",
        type=int,
        default=2000,
        help="total windows to generate"
    )

    parser.add_argument(
        "--window",
        type=int,
        default=16,
        help="input window length"
    )

    parser.add_argument(
        "--horizon",
        type=int,
        default=5,
        help="steps ahead to forecast"
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=8
    )

    parser.add_argument(
        "--batch_size",
        type=int,
        default=8,
        help="quantum layer processes samples individually"
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=0.01
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=0
    )

    parser.add_argument(
        "--diff_method",
        type=str,
        default="parameter-shift",
        choices=[
            "parameter-shift",
            "backprop"
        ]
    )

    parser.add_argument(
        "--out_dir",
        type=str,
        default="./results"
    )

    args = parser.parse_args()

    # ========================================================
    # Dependency check
    # ========================================================

    if not HAVE_PENNYLANE:

        raise SystemExit(
            "\nPennyLane is not installed.\n\n"
            "Install it with:\n"
            "    python -m pip install pennylane\n"
        )

    # ========================================================
    # Directories and seeds
    # ========================================================

    os.makedirs(
        args.out_dir,
        exist_ok=True
    )

    torch.manual_seed(
        args.seed
    )

    np.random.seed(
        args.seed
    )

    # ========================================================
    # Dataset
    # ========================================================

    print(
        "\nGenerating higher-order nonlinear synthetic dataset..."
    )

    X, y = build_dataset(
        n_samples=args.samples,
        window=args.window,
        horizon=args.horizon,
        seed=args.seed
    )

    split = int(
        0.8 * len(X)
    )

    X_train = X[:split]
    X_test = X[split:]

    y_train = y[:split]
    y_test = y[split:]

    print(
        f"Train samples : {len(X_train)}"
    )

    print(
        f"Test samples  : {len(X_test)}"
    )

    print(
        f"Window        : {args.window}"
    )

    print(
        f"Horizon       : {args.horizon}"
    )

    print(
        "Label balance :",
        np.bincount(
            y_train,
            minlength=3
        )
    )

    # ========================================================
    # Quantum circuit
    # ========================================================

    print(
        f"\nCreating quantum circuit "
        f"(diff_method={args.diff_method})..."
    )

    qnode = make_qnode(
        diff_method=args.diff_method
    )

    # ========================================================
    # Models
    # ========================================================

    models = {

        "Hybrid_QML":
            HybridQMLModel(
                qnode
            ),

        "Classical_LSTM":
            ClassicalLSTMBaseline(),

        "Classical_MLP":
            ClassicalMLPBaseline(
                window=args.window
            ),
    }

    # ========================================================
    # Training
    # ========================================================

    all_logs = {}
    summaries = []

    total_start = time.perf_counter()

    for name, model in models.items():

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"Training {name}"
        )

        print(
            "=" * 70
        )

        model_start = time.perf_counter()

        rows, summary = train_and_log(
            name,
            model,
            X_train,
            y_train,
            X_test,
            y_test,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            out_dir=args.out_dir
        )

        model_time = (
            time.perf_counter()
            - model_start
        )

        print(
            f"\n{name} completed in "
            f"{model_time:.2f} seconds"
        )

        all_logs[name] = rows

        summaries.append(
            summary
        )

    total_time = (
        time.perf_counter()
        - total_start
    )

    # ========================================================
    # Results
    # ========================================================

    print(
        "\nGenerating plots..."
    )

    plot_curves(
        all_logs,
        args.out_dir
    )

    plot_latency_vs_params(
        summaries,
        args.out_dir
    )

    csv_path, md_path = (
        write_summary_table(
            summaries,
            args.out_dir
        )
    )

    # ========================================================
    # Final summary
    # ========================================================

    print(
        "\n"
        + "=" * 70
    )

    print(
        "FINAL SUMMARY"
    )

    print(
        "=" * 70
    )

    for s in summaries:

        print(
            f"\nModel: {s['model']}"
        )

        print(
            f"  Parameters : "
            f"{s['total_trainable_params']}"
        )

        print(
            f"  Test loss  : "
            f"{s['final_test_loss']:.4f}"
        )

        print(
            f"  Test acc   : "
            f"{s['final_test_acc']:.3f}"
        )

        print(
            f"  Step time  : "
            f"{s['avg_step_time_ms']:.2f} ms"
        )

        print(
            f"  Peak memory: "
            f"{s['peak_memory_kb']:.1f} KB"
        )

    print(
        f"\nTotal benchmark time: "
        f"{total_time:.2f} seconds"
    )

    print(
        f"\nResults written to:"
        f"\n  {args.out_dir}"
    )

    print(
        f"\nSummary CSV:"
        f"\n  {csv_path}"
    )

    print(
        f"\nSummary Markdown:"
        f"\n  {md_path}"
    )


if __name__ == "__main__":
    main()
