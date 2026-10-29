"""Benchmark Formulon Physics' actual Legendre encoder/decoder.

Author: Sri Kaleeswarar S
ORCID: 0009-0005-6360-2345

AI assistance disclosure
------------------------
Generative AI (OpenAI ChatGPT) assisted in drafting and documenting this
benchmark script. Sri Kaleeswarar S is responsible for verifying the code,
running the experiments, interpreting the outputs, and approving any claims.

Purpose
-------
This script calls the published Formulon API directly:
    formulon.quantum_computing.legendre_encoder.legendre_features
    formulon.quantum_computing.legendre_encoder.measure_and_decode

It does not silently replace Formulon's encoder with a separately written
Qiskit circuit. The current Formulon implementation uses PennyLane's
`default.qubit` simulator internally. Google Colab is suitable for running
this benchmark; Qiskit can be used later as an independent cross-check, but it
is not the backend executing the Formulon function in this script.

Outputs
-------
CSV files with raw results and summaries, PNG figures, environment metadata.
No quantum-advantage claim is assumed or tested by this benchmark.
"""

# In Google Colab, run this installation cell first if Formulon is not already
# installed. The optional extra name may vary by published package metadata;
# the explicit PennyLane install ensures the backend dependency is present.
# !pip -q install "formulon-physics==1.0.0" "pennylane" "scipy" "pandas" "numpy" "matplotlib"

# If the package release is not available or you want to test the exact source
# archive you uploaded, upload formulon_physics-1.0.0.tar.gz to Colab and run:
# !pip -q install /content/formulon_physics-1.0.0.tar.gz pennylane scipy pandas matplotlib

import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import eval_legendre

from formulon.quantum_computing.legendre_encoder import (
    legendre_features,
    measure_and_decode,
)

AUTHOR = "Sri Kaleeswarar S"
ORCID = "0009-0005-6360-2345"
RANDOM_SEED = 20261028
OUTPUT_DIR = Path("formulon_legendre_benchmark_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# Start with a manageable development run. For a final study, increase
# REPETITIONS (for example, to 30 or 100) after checking runtime.
X_VALUES = np.linspace(-1.0, 1.0, 41)
DEGREES = [2, 4, 6, 8, 12]
SHOT_LEVELS = [100, 500, 1000, 5000]
REPETITIONS = 5


def classical_features(x: float, degree: int) -> np.ndarray:
    """Compute SciPy reference values P_0(x), ..., P_(degree-1)(x)."""
    return np.asarray([eval_legendre(n, x) for n in range(degree)], dtype=float)


def check_formulon_against_scipy(x_values, degrees) -> pd.DataFrame:
    """Check Formulon's deterministic Legendre features against SciPy.

    This is a zero-shot mathematical implementation check. It verifies that
    Formulon's recurrence returns the same Legendre values as SciPy before we
    investigate finite-shot measurement statistics.
    """
    rows = []
    for x in x_values:
        for degree in degrees:
            formulon_values = np.asarray(legendre_features(float(x), degree))
            scipy_values = classical_features(float(x), degree)
            for n in range(degree):
                rows.append({
                    "x": float(x),
                    "requested_degree": degree,
                    "polynomial_order": n,
                    "formulon_value": float(formulon_values[n]),
                    "scipy_value": float(scipy_values[n]),
                    "absolute_difference": float(abs(formulon_values[n] - scipy_values[n])),
                })
    result = pd.DataFrame(rows)
    result.to_csv(OUTPUT_DIR / "deterministic_formulon_vs_scipy.csv", index=False)
    return result


def run_formulon_benchmark() -> pd.DataFrame:
    """Run finite-shot measurements by calling Formulon's public API.

    Each call to `measure_and_decode` constructs and executes the actual
    Formulon/PennyLane circuit. The returned `z_expectations` are estimates of
    the Legendre features; `decoded_x` is Formulon's reconstructed input.
    """
    records = []
    total = len(X_VALUES) * len(DEGREES) * len(SHOT_LEVELS) * REPETITIONS
    completed = 0
    start = time.time()

    for x_index, x in enumerate(X_VALUES):
        for degree in DEGREES:
            # The deterministic feature vector is the target for the measured
            # Z expectations. The final component is P_(degree-1)(x).
            target_features = classical_features(float(x), degree)

            for shots in SHOT_LEVELS:
                for repetition in range(REPETITIONS):
                    # Different deterministic seeds give reproducible but
                    # independent pseudo-random shot samples for each run.
                    seed = (
                        RANDOM_SEED
                        + x_index * 100000
                        + degree * 1000
                        + shots * 10
                        + repetition
                    )

                    measurement = measure_and_decode(
                        x=float(x),
                        degree=int(degree),
                        shots=int(shots),
                        xmin=-1.0,
                        xmax=1.0,
                        seed=int(seed),
                    )

                    measured_features = np.asarray(measurement.z_expectations, dtype=float)
                    decoded_x = float(measurement.decoded_x)

                    # One row per trial preserves raw feature-level results.
                    for order in range(degree):
                        error = measured_features[order] - target_features[order]
                        records.append({
                            "x": float(x),
                            "degree": int(degree),
                            "shots": int(shots),
                            "repetition": int(repetition),
                            "seed": int(seed),
                            "polynomial_order": int(order),
                            "true_feature": float(target_features[order]),
                            "measured_feature": float(measured_features[order]),
                            "signed_feature_error": float(error),
                            "absolute_feature_error": float(abs(error)),
                            "squared_feature_error": float(error * error),
                            "decoded_x": decoded_x,
                            "decoded_x_absolute_error": abs(decoded_x - float(x)),
                        })

                    completed += 1
        print(f"Completed x={x:+.3f}; {completed}/{total} Formulon calls finished")

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / "formulon_raw_results.csv", index=False)
    print(f"Completed in {time.time() - start:.1f} seconds")
    return df


def summarize_feature_accuracy(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize measured feature error by requested degree and shot count."""
    summary = (
        df.groupby(["degree", "shots"])
        .agg(
            feature_mae=("absolute_feature_error", "mean"),
            feature_rmse=("squared_feature_error", lambda s: float(np.sqrt(np.mean(s)))),
            feature_max_absolute_error=("absolute_feature_error", "max"),
            feature_bias=("signed_feature_error", "mean"),
            decoded_x_mae=("decoded_x_absolute_error", "mean"),
            decoded_x_rmse=("decoded_x_absolute_error", lambda s: float(np.sqrt(np.mean(np.square(s))))),
            decoded_x_max_absolute_error=("decoded_x_absolute_error", "max"),
            n_feature_records=("measured_feature", "count"),
        )
        .reset_index()
    )
    summary.to_csv(OUTPUT_DIR / "summary_by_degree_and_shots.csv", index=False)
    return summary


def plot_rmse_vs_shots(summary: pd.DataFrame) -> None:
    """Plot feature and decoded-input RMSE as functions of shot count."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for degree in DEGREES:
        part = summary[summary["degree"] == degree]
        axes[0].plot(part["shots"], part["feature_rmse"], marker="o", label=f"degree={degree}")
        axes[1].plot(part["shots"], part["decoded_x_rmse"], marker="o", label=f"degree={degree}")
    for ax in axes:
        ax.set_xscale("log")
        ax.set_xlabel("Measurement shots")
        ax.grid(alpha=0.25)
        ax.legend()
    axes[0].set_ylabel("RMSE of Legendre feature estimates")
    axes[0].set_title("Feature reconstruction error")
    axes[1].set_ylabel("RMSE of decoded x")
    axes[1].set_title("Input reconstruction error")
    fig.suptitle("Formulon Legendre encoder: accuracy versus shot count")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "figure_rmse_vs_shots.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_feature_reconstruction(df: pd.DataFrame, degree: int = 6, shots: int = 5000) -> None:
    """Plot measured mean feature values against the SciPy targets."""
    part = df[(df["degree"] == degree) & (df["shots"] == shots)]
    means = (
        part.groupby(["x", "polynomial_order"])
        .agg(true_feature=("true_feature", "first"), measured_mean=("measured_feature", "mean"))
        .reset_index()
    )
    orders = sorted(means["polynomial_order"].unique())
    fig, axes = plt.subplots(len(orders), 1, figsize=(8, 2.2 * len(orders)), sharex=True)
    if len(orders) == 1:
        axes = [axes]
    for ax, order in zip(axes, orders):
        p = means[means["polynomial_order"] == order]
        ax.plot(p["x"], p["true_feature"], label=f"SciPy P_{order}(x)")
        ax.plot(p["x"], p["measured_mean"], marker=".", linestyle="", label="Formulon measured mean")
        ax.set_ylabel(f"P_{order}")
        ax.grid(alpha=0.25)
        ax.legend(loc="best")
    axes[-1].set_xlabel("x")
    fig.suptitle(f"Formulon feature reconstruction: degree={degree}, shots={shots}")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "figure_feature_reconstruction.png", dpi=300, bbox_inches="tight")
    plt.show()


def save_metadata() -> None:
    """Save author, environment, and configuration metadata beside the data."""
    import scipy
    try:
        import pennylane as qml
        pennylane_version = qml.__version__
    except Exception:
        pennylane_version = "unavailable"
    try:
        import formulon
        formulon_version = getattr(formulon, "__version__", "check package metadata")
    except Exception:
        formulon_version = "unknown"

    metadata = {
        "author": AUTHOR,
        "orcid": ORCID,
        "package": "Formulon Physics",
        "formulon_version": formulon_version,
        "implementation_under_test": "formulon.quantum_computing.legendre_encoder.measure_and_decode",
        "quantum_backend_used_by_formulon": "PennyLane default.qubit",
        "python_version": sys.version,
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scipy_version": scipy.__version__,
        "pennylane_version": pennylane_version,
        "x_points": len(X_VALUES),
        "degrees": DEGREES,
        "shot_levels": SHOT_LEVELS,
        "repetitions": REPETITIONS,
        "seed_base": RANDOM_SEED,
        "ai_assistance_disclosure": (
            "Generative AI (OpenAI ChatGPT) assisted in drafting and documenting this benchmark. "
            "The author is responsible for verification, execution, interpretation, and conclusions."
        ),
    }
    (OUTPUT_DIR / "benchmark_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    print("Author:", AUTHOR)
    print("ORCID:", ORCID)
    print("Testing Formulon's own implementation, not a replacement Qiskit circuit.")

    # Step 1: verify deterministic Formulon features against an independent
    # SciPy reference before running any shot-based quantum measurements.
    deterministic_df = check_formulon_against_scipy(X_VALUES, DEGREES)
    max_difference = deterministic_df["absolute_difference"].max()
    print(f"Maximum deterministic Formulon-vs-SciPy difference: {max_difference:.3e}")

    # Step 2: run the actual Formulon/PennyLane finite-shot encoder and decoder.
    raw_df = run_formulon_benchmark()

    # Step 3: compute summaries and figures from the saved raw data.
    summary_df = summarize_feature_accuracy(raw_df)
    print(summary_df.to_string(index=False))
    plot_rmse_vs_shots(summary_df)
    plot_feature_reconstruction(raw_df, degree=6, shots=5000)
    save_metadata()

    print("\nBenchmark finished. Inspect all CSVs/plots before drawing conclusions.")
    print("Output folder:", OUTPUT_DIR.resolve())
