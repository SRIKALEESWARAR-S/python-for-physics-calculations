# ==============================================================================
#  Physics-Informed Quantum Autoencoder (PI-QAE) & Quantum State Reverser
#  ------------------------------------------------------------------------------
#  Developed by: Sri Kaleeswarar Open Science Labs
#  License: MIT License
#  
#  Copyright (c) 2026 Sri Kaleeswarar Open Science Labs
#  
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software").
# ==============================================================================


import serial
import time
import numpy as np
import torch
import torch.nn as nn
import pennylane as qml
from scipy.special import roots_legendre
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import matplotlib.font_manager as fm
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# ==========================================
# 1. Configuration
# ==========================================
WINDOW_SIZE = 100       
N_LEGENDRE = 8          
N_QUBITS = 4            
N_LAYERS = 3            
LEARNING_RATE = 0.02

SERIAL_PORT = '/dev/ttyUSB0'  # Adjust to your Arduino Port
BAUD_RATE = 9600

# ==========================================
# 2. Classical Preprocessing
# ==========================================
def extract_legendre_coefficients(t, signal, n_coeffs=8):
    t_scaled = 2 * (t - t.min()) / (t.max() - t.min() + 1e-9) - 1
    roots, weights = roots_legendre(len(t))
    signal_interp = np.interp(roots, t_scaled, signal)
    
    coeffs = []
    for n in range(n_coeffs):
        Pn = np.polynomial.legendre.Legendre.basis(n)(roots)
        c_n = ((2 * n + 1) / 2) * np.sum(weights * signal_interp * Pn)
        coeffs.append(c_n)
        
    return torch.tensor(coeffs, dtype=torch.float32)

# ==========================================
# 3. Physics Layer
# ==========================================
class DynamicPhysicsCoupling(nn.Module):
    def __init__(self, n_legendre, n_qubits):
        super().__init__()
        self.kg_momentum = nn.Parameter(torch.rand(n_legendre, dtype=torch.float32))
        self.kg_mass = nn.Parameter(torch.rand(1, dtype=torch.float32))
        self.cg_coupling = nn.Linear(n_legendre, n_qubits, bias=False)
        nn.init.orthogonal_(self.cg_coupling.weight)

    def forward(self, c_n, t_evolve=1.0):
        omega = torch.sqrt(self.kg_momentum**2 + self.kg_mass**2)
        kg_state = c_n * torch.cos(omega * t_evolve)
        coupled_angles = self.cg_coupling(kg_state)
        return torch.tanh(coupled_angles) * np.pi

# ==========================================
# 4. Advanced Quantum Circuit
# ==========================================
dev = qml.device("default.qubit", wires=N_QUBITS)

@qml.qnode(dev, interface="torch")
def quantum_reverser_circuit(encoded_angles, unitary_weights, phase_shifts):
    """
    Advanced Multi-Layer Quantum Architecture modeling real physical phenomena.
    """
    # 1. Superposition Layer: Spread the initial state across all possibilities
    for w in range(N_QUBITS):
        qml.Hadamard(wires=w)

    # 2. Data Injection Layer: Embed the analog LED signal
    qml.AngleEmbedding(encoded_angles, wires=range(N_QUBITS), rotation='Y')
    
    # 3. Dynamic Interference Layer: Trainable multi-qubit entanglement
    qml.StronglyEntanglingLayers(unitary_weights, wires=range(N_QUBITS))
    
    # 4. Phase Shift Layer: Simulates wave dispersion phenomena
    for w in range(N_QUBITS):
        qml.PhaseShift(phase_shifts[w], wires=w)
        
    # 5. Wave Function Collapse Layer: Force measurement to real probability distributions
    return qml.probs(wires=range(N_QUBITS))

class PhotoelectricQuantumReverser(nn.Module):
    def __init__(self, n_legendre, n_qubits, n_layers):
        super().__init__()
        self.physics_layer = DynamicPhysicsCoupling(n_legendre, n_qubits)
        
        weight_shape = qml.StronglyEntanglingLayers.shape(n_layers=n_layers, n_wires=n_qubits)
        self.unitary_weights = nn.Parameter(torch.randn(weight_shape, dtype=torch.float32, requires_grad=True))
        
        # New trainable phase shift parameters
        self.phase_shifts = nn.Parameter(torch.zeros(n_qubits, dtype=torch.float32, requires_grad=True))
        
    def forward(self, legendre_coeffs):
        angles = self.physics_layer(legendre_coeffs)
        probabilities = quantum_reverser_circuit(angles, self.unitary_weights, self.phase_shifts)
        return probabilities

# ==========================================
# 5. Circuit Visualization Tool
# ==========================================
def display_quantum_circuit(model):
    """Draws and prints the structural architecture of the quantum circuit."""
    print("\n" + "="*70)
    print(" ஶ்ரீகாளீஸ்வரர் குவாண்டம் இயற்பியல் படைப்பு - CIRCUIT ARCHITECTURE")
    print("="*70)
    
    dummy_angles = torch.rand(N_QUBITS)
    
    # Render the PennyLane circuit as an ASCII text diagram
    circuit_diagram = qml.draw(quantum_reverser_circuit)(
        dummy_angles, 
        model.unitary_weights.detach(), 
        model.phase_shifts.detach()
    )
    print(circuit_diagram)
    print("======================================================================\n")

# ==========================================
# 6. Dashboard & Dynamic Training Setup
# ==========================================
# ==========================================
# 6. Dashboard & Dynamic Training Setup
# ==========================================
def main():
    raw_data_buffer = deque([0.5] * WINDOW_SIZE, maxlen=WINDOW_SIZE)
    time_buffer = deque(np.linspace(0, 1, WINDOW_SIZE), maxlen=WINDOW_SIZE)

    # Serial Connection
    arduino = None
    try:
        arduino = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=0.01)
        time.sleep(1.5)
        arduino.reset_input_buffer()
        print(f"✅ HARDWARE CONNECTED: Streaming from {SERIAL_PORT}")
    except Exception:
        print(f"⚠️ HARDWARE NOT FOUND on {SERIAL_PORT}. Using SYNTHETIC stream.")

    # Model Initialization
    model = PhotoelectricQuantumReverser(N_LEGENDRE, N_QUBITS, N_LAYERS)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Render Circuit to Terminal before starting UI
    display_quantum_circuit(model)
    time.sleep(2)

    # Setup Plot
    plt.style.use('dark_background')
    fig, (ax_signal, ax_spectrum) = plt.subplots(1, 2, figsize=(15, 6))
    
    # ---> TAMIL TEXT HEADER WITH MULTIPLE FONT FALLBACKS <---
    # Updated Font Hierarchy for Linux / Ubuntu
    tamil_fonts = ['Noto Sans Tamil', 'Lohit Tamil', 'DejaVu Sans', 'sans-serif']

    fig.suptitle("ஶ்ரீகாளீஸ்வரர் குவாண்டம் இயற்பியல் படைப்பு", 
             fontsize=20, color='#FFD700', fontweight='bold', fontname=tamil_fonts)
    
    fig.canvas.manager.set_window_title("Sri Kaleeswarar Open Science Labs - PI-QAE")
    fig.subplots_adjust(top=0.85, bottom=0.15) 

    # Left Plot (Signal)
    ax_signal.set_title("Classical LED Signal Dynamics", color='#00FF66')
    ax_signal.set_ylim(-0.2, 1.2)
    line_raw, = ax_signal.plot([], [], color='#00FF66', lw=2, label="Raw LED Input")
    line_recon, = ax_signal.plot([], [], color='#00E5FF', lw=1.5, linestyle=':', label="Legendre Wave Reconstruction")
    ax_signal.legend(loc="upper right")
    ax_signal.grid(True, color='#222222', linestyle='--')

    source_badge = ax_signal.text(
        0.03, 0.90, '', transform=ax_signal.transAxes, fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='black', alpha=0.8, edgecolor='white')
    )

    # Right Plot (Quantum Wave Function)
    ax_spectrum.set_title("Wave Function Collapse $P(|i\\rangle)$", color='#FF007F')
    ax_spectrum.set_ylim(0, 0.5)
    
    # 4 Qubits = 2^4 = 16 Basis States
    num_states = 2**N_QUBITS
    x_bars = np.arange(num_states)
    bars = ax_spectrum.bar(x_bars, np.zeros(num_states), color='#FF007F', alpha=0.8)
    ax_spectrum.grid(True, color='#222222', linestyle='--')

    loss_text = ax_spectrum.text(0.5, 0.9, '', transform=ax_spectrum.transAxes, 
                                 color='white', fontsize=12, ha='center')

    frame_counter = [0]

    def update(frame):
        frame_counter[0] += 1
        using_arduino = False
        
        # Drain Serial Buffer
        if arduino:
            while arduino.in_waiting > 0:
                try:
                    line = arduino.readline().decode('utf-8').strip()
                    if line:
                        val = float(line) / 1023.0 
                        raw_data_buffer.append(val)
                        using_arduino = True
                except ValueError:
                    pass

        if not using_arduino and not arduino:
            synthetic_val = 0.5 + 0.3 * np.sin(frame * 0.1) + np.random.normal(0, 0.02)
            raw_data_buffer.append(synthetic_val)

        # Update Badge
        if using_arduino:
            source_badge.set_text("● SOURCE: ARDUINO UNO")
            source_badge.set_color('#00FF66')
            source_badge.get_bbox_patch().set_edgecolor('#00FF66')
        else:
            source_badge.set_text("▲ SOURCE: SYNTHETIC STREAM")
            source_badge.set_color('#FF3333')
            source_badge.get_bbox_patch().set_edgecolor('#FF3333')

        y_raw = np.array(raw_data_buffer, dtype=np.float32)
        t_arr = np.array(time_buffer, dtype=np.float32)

        # 1. Classical Feature Extraction (8 features)
        c_n = extract_legendre_coefficients(t_arr, y_raw, n_coeffs=N_LEGENDRE)
        
        # --- FIX FOR TENSOR MISMATCH ---
        # Map 8 Legendre classical features into a 16-dimensional quantum space
        # by zero-padding the higher-order states to create our target distribution.
        c_n_padded = torch.zeros(num_states, dtype=torch.float32)
        max_idx = min(N_LEGENDRE, num_states)
        c_n_padded[:max_idx] = c_n[:max_idx]
        
        # Softmax ensures it forms a valid probability distribution summing to 1.0
        target_dist = torch.softmax(c_n_padded, dim=0)

        # 2. Model Inference & Training Step
        optimizer.zero_grad()
        probs_out = model(c_n)
        loss = torch.nn.functional.mse_loss(probs_out, target_dist)
        loss.backward()
        optimizer.step()

        # Terminal Log
        if frame_counter[0] % 10 == 0:
            src = "ARDUINO" if using_arduino else "SYNTHETIC"
            print(f"[{src} | Frame {frame_counter[0]:04d}] Phase Shift [0]: {model.phase_shifts[0].item():.3f} | Loss: {loss.item():.6f}")

        # Signal Reconstruction for Visualization
        roots = np.linspace(-1, 1, WINDOW_SIZE)
        y_recon = np.zeros(WINDOW_SIZE)
        c_n_np = c_n.detach().numpy()
        for n in range(N_LEGENDRE):
            Pn = np.polynomial.legendre.Legendre.basis(n)(roots)
            y_recon += c_n_np[n] * Pn

        # Update Graphics
        line_raw.set_data(t_arr, y_raw)
        line_recon.set_data(t_arr, y_recon)
        ax_signal.set_xlim(t_arr.min(), t_arr.max())
        
        probs_np = probs_out.detach().cpu().numpy()
        for bar, val in zip(bars, probs_np):
            bar.set_height(val)
            
        loss_text.set_text(f'Collapse Target Loss: {loss.item():.6f}')
            
        return [line_raw, line_recon, loss_text, source_badge] + list(bars)

    # Fixed cache_frame_data warning by passing cache_frame_data=False
    ani = FuncAnimation(fig, update, interval=30, blit=False, cache_frame_data=False)
    plt.show()

if __name__ == "__main__":
    main()
