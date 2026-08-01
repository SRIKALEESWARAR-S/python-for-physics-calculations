import csv
import numpy as np
import pandas as pd
import scipy.special as special
import scipy.linalg as linalg
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity

# =====================================================================
# LAYER 1: ASCII Information Encoding
# =====================================================================
def text_to_ascii_signal(text: str) -> np.ndarray:
    ascii_vals = np.array([ord(char) for char in text], dtype=float)
    return (ascii_vals - 127.5) / 127.5

def ascii_signal_to_text(signal_vals: np.ndarray) -> str:
    denorm = np.round(signal_vals * 127.5 + 127.5)
    denorm = np.clip(denorm, 0, 255).astype(int)
    return "".join([chr(val) for val in denorm])

# =====================================================================
# LAYER 2: 1D Wave Equation Simulation (Acoustic Carrier)
# =====================================================================
def solve_wave_equation(nx=64, nt=50, c=1.0, dx=0.1, dt=0.05):
    u = np.zeros((nt, nx))
    x = np.linspace(-2, 2, nx)
    u[0, :] = np.exp(-x**2)
    u[1, :] = u[0, :]
    
    r = (c * dt / dx) ** 2
    for n in range(1, nt - 1):
        for i in range(1, nx - 1):
            u[n+1, i] = 2*(1 - r)*u[n, i] + r*(u[n, i+1] + u[n, i-1]) - u[n-1, i]
    return u[-1, :]

# =====================================================================
# LAYER 14: Automated CSV & XLSX Metrics Exporter
# =====================================================================
def export_pipeline_metrics(
    secret_msg: str,
    reconstructed_text: str,
    fidelity: float,
    payload: np.ndarray,
    decoded_payload: np.ndarray,
    legendre_coeff: np.ndarray,
    wave_frame: np.ndarray,
    legendre_wave: np.ndarray,
    bessel_shaped: np.ndarray,
    psi_amplitude: np.ndarray,
    final_sv_data: np.ndarray,
    qft_init_data: np.ndarray,
    qft_fin_data: np.ndarray,
    filename_prefix: str = "quantum_pipeline_export"
):
    """
    Exports all calculated mathematical, acoustic, and quantum metrics
    into CSV files and a multi-tab Excel Workbook (.xlsx).
    """
    # 1. General Pipeline Summary
    summary_data = {
        "Metric": [
            "Input Secret Message",
            "Reconstructed Message",
            "Exact Match",
            "Quantum Register Size (Qubits)",
            "Hilbert Space Dimension",
            "Quantum State Fidelity",
            "Legendre Coeff a3 (x^3)",
            "Legendre Coeff a2 (x^2)",
            "Legendre Coeff a1 (x^1)",
            "Legendre Coeff a0 (Constant)",
        ],
        "Value": [
            secret_msg,
            reconstructed_text,
            secret_msg == reconstructed_text,
            len(payload),
            len(psi_amplitude),
            f"{fidelity:.8f}",
            f"{legendre_coeff[0]:.6f}",
            f"{legendre_coeff[1]:.6f}",
            f"{legendre_coeff[2]:.6f}",
            f"{legendre_coeff[3]:.6f}",
        ]
    }
    df_summary = pd.DataFrame(summary_data)

    # 2. Per-Qubit / Character Quantum Phase Shift Log
    num_chars = len(secret_msg)
    qubit_log = []
    for i in range(num_chars):
        idx_i = 2**i
        applied_phase_rad = payload[i] * (np.pi / 4.0)
        qft_init_phase = np.angle(qft_init_data[idx_i])
        qft_fin_phase = np.angle(qft_fin_data[idx_i])
        recovered_phase_diff = (qft_fin_phase - qft_init_phase + np.pi) % (2 * np.pi) - np.pi

        qubit_log.append({
            "Qubit_Index": i,
            "Char": secret_msg[i],
            "ASCII_Normalized_Input": payload[i],
            "Applied_Rz_Phase_Rad": applied_phase_rad,
            "QFT_Initial_Phase_Rad": qft_init_phase,
            "QFT_Final_Phase_Rad": qft_fin_phase,
            "Recovered_Phase_Diff_Rad": recovered_phase_diff,
            "Decoded_Signal_Val": decoded_payload[i],
            "Reconstructed_Char": reconstructed_text[i],
        })
    df_qubits = pd.DataFrame(qubit_log)

    # 3. Continuous Field & Quantum Register State Array
    dim = len(psi_amplitude)
    nx = len(wave_frame)
    max_len = max(dim, nx)

    def pad_array(arr, target_len):
        padded = np.full(target_len, np.nan)
        padded[:len(arr)] = arr
        return padded

    vector_data = {
        "Index": np.arange(max_len),
        "Acoustic_Wave_u(x)": pad_array(wave_frame, max_len),
        "Legendre_Fit": pad_array(legendre_wave, max_len),
        "Bessel_Shaped_Signal": pad_array(bessel_shaped, max_len),
        "Quantum_State_Index": [i if i < dim else np.nan for i in range(max_len)],
        "Initial_Amplitude_Re": pad_array(np.real(psi_amplitude), max_len),
        "Initial_Amplitude_Im": pad_array(np.imag(psi_amplitude), max_len),
        "Initial_Probability": pad_array(np.abs(psi_amplitude)**2, max_len),
        "Final_Amplitude_Re": pad_array(np.real(final_sv_data), max_len),
        "Final_Amplitude_Im": pad_array(np.imag(final_sv_data), max_len),
        "Final_Probability": pad_array(np.abs(final_sv_data)**2, max_len),
    }
    df_vectors = pd.DataFrame(vector_data)

    # File Exports
    df_summary.to_csv(f"{filename_prefix}_summary.csv", index=False)
    df_qubits.to_csv(f"{filename_prefix}_qubit_phase_log.csv", index=False)
    df_vectors.to_csv(f"{filename_prefix}_statevector_data.csv", index=False)

    excel_path = f"{filename_prefix}_complete.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Pipeline Summary", index=False)
        df_qubits.to_excel(writer, sheet_name="Qubit Phase Log", index=False)
        df_vectors.to_excel(writer, sheet_name="Field & Statevector Data", index=False)

    print(f"\n[*] Layer 14 Complete:")
    print(f"    - CSV exports: '{filename_prefix}_summary.csv', '{filename_prefix}_qubit_phase_log.csv', '{filename_prefix}_statevector_data.csv'")
    print(f"    - Excel export: '{excel_path}'")

# =====================================================================
# MAIN PIPELINE EXECUTION
# =====================================================================
def run_quantum_audio_pipeline(secret_msg: str):
    print(f"[*] Input Secret Message: '{secret_msg}'")
    
    # Layer 1: ASCII Conversion
    payload = text_to_ascii_signal(secret_msg)
    num_chars = len(payload)
    
    # Layer 2: Wave Equation Carrier
    wave_frame = solve_wave_equation(nx=64)
    
    # Layer 3: Legendre Polynomial Expansion
    x_grid = np.linspace(-1, 1, len(wave_frame))
    legendre_coeff = np.polyfit(x_grid, wave_frame, deg=3)
    legendre_wave = np.polyval(legendre_coeff, x_grid)
    
    # Layer 4: Bessel Function Frequency/Phase Modulation
    bessel_shaped = legendre_wave * special.jv(0, np.abs(legendre_wave) * 5.0)
    
    # Layer 5 & 6: Hankel Matrix & Markovian Transition Matrix
    L = len(bessel_shaped) // 2
    hankel_mat = linalg.hankel(bessel_shaped[:L], bessel_shaped[L-1:])
    abs_hankel = np.abs(hankel_mat) + 1e-8
    markov_mat = abs_hankel / abs_hankel.sum(axis=1, keepdims=True)
    
    # Layer 7 & 8: Superposition & Quantum Register Initialization
    num_qubits = max(3, num_chars)
    dim = 2 ** num_qubits
    
    if len(bessel_shaped) < dim:
        raw_state = np.pad(bessel_shaped, (0, dim - len(bessel_shaped)), 'constant')
    else:
        raw_state = bessel_shaped[:dim]
        
    psi_amplitude = raw_state / np.linalg.norm(raw_state)
    print(f"[*] Encoding into {num_qubits}-Qubit Quantum Register (Dimension {dim})")
    
    qc = QuantumCircuit(num_qubits)
    qc.initialize(psi_amplitude, range(num_qubits))
    initial_sv = Statevector.from_instruction(qc)
    
    # Layer 9: Quantum Fourier Transform (QFT)
    qft_gate = QFT(num_qubits=num_qubits, do_swaps=True).to_gate()
    qc.append(qft_gate, range(num_qubits))
    qft_initial_sv = Statevector.from_instruction(qc)
    
    # Layer 10: Phase Perturbation / Steganographic Rotation
    for i in range(num_chars):
        phase_shift = payload[i] * (np.pi / 4.0)
        qc.rz(phase_shift, i)
    qft_final_sv = Statevector.from_instruction(qc)
    
    # Layer 11: Inverse Quantum Fourier Transform (IQFT)
    iqft_gate = QFT(num_qubits=num_qubits, do_swaps=True, inverse=True).to_gate()
    qc.append(iqft_gate, range(num_qubits))
    
    # Layer 12: Statevector Evaluation & Fidelity
    final_sv = Statevector.from_instruction(qc)
    fidelity = state_fidelity(initial_sv, final_sv)
    print(f"[*] Quantum State Fidelity after Phase Shift: {fidelity:.6f}")
    
    # Layer 13: Phase Recovery & ASCII Reconstruction
    qft_init_data = qft_initial_sv.data
    qft_fin_data = qft_final_sv.data
    
    decoded_payload = []
    for i in range(num_chars):
        idx_i = 2**i
        idx_0 = 0
        dphi_i = np.angle(qft_fin_data[idx_i]) - np.angle(qft_init_data[idx_i])
        dphi_0 = np.angle(qft_fin_data[idx_0]) - np.angle(qft_init_data[idx_0])
        diff = (dphi_i - dphi_0 + np.pi) % (2 * np.pi) - np.pi
        decoded_payload.append(diff * (4.0 / np.pi))
        
    reconstructed_text = ascii_signal_to_text(np.array(decoded_payload))
    print(f"[*] Reconstructed Message: '{reconstructed_text}'")

    # Layer 14: Data & Metrics Export
    export_pipeline_metrics(
        secret_msg=secret_msg,
        reconstructed_text=reconstructed_text,
        fidelity=fidelity,
        payload=payload,
        decoded_payload=np.array(decoded_payload),
        legendre_coeff=legendre_coeff,
        wave_frame=wave_frame,
        legendre_wave=legendre_wave,
        bessel_shaped=bessel_shaped,
        psi_amplitude=psi_amplitude,
        final_sv_data=final_sv.data,
        qft_init_data=qft_init_data,
        qft_fin_data=qft_fin_data
    )

    # Visualization
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(wave_frame, label=r'Wave Equation $u(x, t)$', color='blue')
    plt.plot(legendre_wave, label='Legendre Fit', linestyle='--', color='orange')
    plt.title("Layers 2 & 3: Wave Propagation & Legendre Expansion")
    plt.grid(True)
    plt.legend()
    
    plt.subplot(2, 2, 2)
    plt.imshow(markov_mat, cmap='viridis')
    plt.colorbar()
    plt.title("Layer 6: Markovian Transition Matrix")
    
    plt.subplot(2, 2, 3)
    plt.plot(np.abs(psi_amplitude)**2, 'o-', label=r'Initial $|\psi_{in}|^2$', color='green')
    plt.plot(np.abs(final_sv.data)**2, 's--', label=r'Final $|\psi_{out}|^2$', color='red')
    plt.title("Layer 8 & 12: Probability Density Collapse")
    plt.grid(True)
    plt.legend()
    
    plt.subplot(2, 2, 4)
    try:
        qc.draw(output='mpl', ax=plt.gca())
    except Exception:
        plt.text(0.1, 0.5, str(qc.draw(output='text')), fontsize=8, family='monospace')
        plt.axis('off')
    plt.title("Layers 8-11: Qiskit Quantum Circuit")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_quantum_audio_pipeline("sri")
