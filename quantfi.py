import math
import time
import sys
import numpy as np
import torch
import torch.nn as nn
import pennylane as qml
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.animation import FuncAnimation
from collections import deque
import logging

logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# ==========================================
# Configuration & Hardware Settings
# ==========================================
WINDOW_SIZE = 120
N_QUBITS = 4
N_LAYERS = 3
LEARNING_RATE = 0.01
DT = 1e-3

SERIAL_PORT = '/dev/ttyUSB0'  
BAUD_RATE = 9600              

# Initialize PennyLane Native Device
dev = qml.device("default.qubit", wires=N_QUBITS)

# ==========================================
# Quantum Circuit & Model Definition
# ==========================================
def variational_ansatz(weights, wires):
    for l in range(weights.shape[0]):
        for i, w in enumerate(wires):
            qml.RZ(weights[l, i, 0], wires=w)
            qml.RY(weights[l, i, 1], wires=w)
            qml.RZ(weights[l, i, 2], wires=w)
        for i in range(len(wires)):
            qml.CNOT(wires=[wires[i], wires[(i + 1) % len(wires)]])

@qml.qnode(dev, interface="torch", diff_method="parameter-shift")
def rgb_iqft_qnode(inputs, weights):
    # Flatten inputs to safely handle PyTorch batching dynamics
    inputs = inputs.flatten()
    
    wires = list(range(N_QUBITS))
    qml.RY(inputs[0], wires=0)  
    qml.RY(inputs[1], wires=1)  
    qml.RY(inputs[2], wires=2)  
    qml.RY((inputs[0] + inputs[1] + inputs[2]) / 3.0, wires=3)
    
    qml.adjoint(qml.QFT)(wires=wires)
    variational_ansatz(weights, wires)
    
    return (
        qml.expval(qml.PauliZ(0) @ qml.PauliZ(1)),
        *[qml.expval(qml.PauliZ(w)) for w in wires]
    )

class TriColorQuantumReverser(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=3, hidden_size=16, batch_first=True)
        self.to_angles = nn.Sequential(nn.Linear(16, 3), nn.Tanh())
        self.q_layer = qml.qnn.TorchLayer(rgb_iqft_qnode, {"weights": (N_LAYERS, N_QUBITS, 3)})
        self.output_head = nn.Linear(N_QUBITS + 1, 3)

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        rgb_angles = self.to_angles(h_n[-1]) * math.pi
        
        quantum_features = self.q_layer(rgb_angles)
        # CRITICAL FIX: Ensure features are (batch_size, 5) before passing to Linear layer
        quantum_features = quantum_features.view(x.shape[0], -1) 
        
        return self.output_head(quantum_features)

# ==========================================
# Application Runtime & Dashboard
# ==========================================
def main():
    red_buf = deque([0.5] * WINDOW_SIZE, maxlen=WINDOW_SIZE)
    green_buf = deque([0.3] * WINDOW_SIZE, maxlen=WINDOW_SIZE)
    blue_buf = deque([0.8] * WINDOW_SIZE, maxlen=WINDOW_SIZE)
    time_buffer = deque(np.linspace(0, WINDOW_SIZE * DT, WINDOW_SIZE), maxlen=WINDOW_SIZE)

    # Connect Serial
    arduino = None
    try:
        import serial
        arduino = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=0.01)
        time.sleep(1.5)
        arduino.reset_input_buffer()
        print(f"✅ HARDWARE CONNECTED: Streaming from {SERIAL_PORT} @ {BAUD_RATE} Baud\n")
    except Exception as e:
        print(f"⚠️ HARDWARE NOT CONNECTED on {SERIAL_PORT}. Operating in SYNTHETIC Mode.\n")

    model = TriColorQuantumReverser()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()

    # --- UI Layout Setup ---
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 9))
    fig.suptitle("Sri Kaleeswarar S - OSL quantum - 8", fontsize=18, fontweight='bold', color='#00FF66')
    
    gs = GridSpec(3, 2, figure=fig, width_ratios=[1.5, 1])
    
    # Left Column: Independent RGB Graphs
    ax_r = fig.add_subplot(gs[0, 0])
    ax_g = fig.add_subplot(gs[1, 0])
    ax_b = fig.add_subplot(gs[2, 0])
    
    line_r, = ax_r.plot([], [], color='#FF3333', lw=2)
    line_g, = ax_g.plot([], [], color='#00FF66', lw=2)
    line_b, = ax_b.plot([], [], color='#3399FF', lw=2)
    
    for ax, title, color in zip([ax_r, ax_g, ax_b], ["Red Channel (A0)", "Green Channel (A1)", "Blue Channel (A2)"], ['#FF3333', '#00FF66', '#3399FF']):
        ax.set_ylim(-0.1, 1.2)
        ax.set_title(title, color=color, fontsize=10, loc='right')
        ax.grid(True, color='#222222', linestyle='--')
        ax.set_xticks([]) # Hide x-ticks for top graphs to keep it clean

    ax_b.set_xticks(np.linspace(0, WINDOW_SIZE * DT, 5)) # Only bottom graph gets x-axis
    
    # Right Column: Quantum Strategy Logits
    ax_logits = fig.add_subplot(gs[0:2, 1])
    actions = ['Sell (-1)', 'Hold (0)', 'Buy (+1)']
    bars = ax_logits.bar(actions, [0.33, 0.33, 0.33], color=['#E41A1C', '#377EB8', '#4DAF4A'], alpha=0.85)
    ax_logits.set_ylim(-0.1, 1.1)
    ax_logits.set_title("Quantum Strategy Prediction Head", color='#FF007F')
    ax_logits.grid(True, color='#222222', linestyle='--')

    # Right Column Bottom: Information Panel
    ax_info = fig.add_subplot(gs[2, 1])
    ax_info.axis('off')
    info_text = ax_info.text(0.05, 0.5, '', color='white', fontsize=12, va='center', family='monospace')

    frame_counter = [0]
    plt.tight_layout()
    fig.subplots_adjust(top=0.9)

    def update(frame):
        frame_counter[0] += 1
        using_arduino = False
        
        # Read from Hardware
        if arduino:
            while arduino.in_waiting > 0:
                try:
                    line = arduino.readline().decode('utf-8').strip()
                    parts = line.split(',')
                    if len(parts) == 3:
                        red_buf.append(np.clip(float(parts[0]) / 1023.0, 0, 1))
                        green_buf.append(np.clip(float(parts[1]) / 1023.0, 0, 1))
                        blue_buf.append(np.clip(float(parts[2]) / 1023.0, 0, 1))
                        using_arduino = True
                except ValueError:
                    pass

        # Generate Synthetic Data if no hardware
        if not using_arduino and not arduino:
            t_val = frame_counter[0] * 0.1
            red_buf.append(np.clip(0.5 + 0.3 * np.sin(t_val) + np.random.normal(0, 0.02), 0, 1))
            green_buf.append(np.clip(0.4 + 0.25 * np.sin(t_val + 1.0) + np.random.normal(0, 0.02), 0, 1))
            blue_buf.append(np.clip(0.6 + 0.2 * np.cos(t_val * 0.5) + np.random.normal(0, 0.02), 0, 1))

        time_buffer.append(time_buffer[-1] + DT)
        rgb_data = np.column_stack((red_buf, green_buf, blue_buf))[-16:]
        x_input = torch.tensor(rgb_data, dtype=torch.float32).unsqueeze(0)

        # Dynamic Target Definition based on signal ratios
        ratio = blue_buf[-1] / (red_buf[-1] + 1e-6)
        target_action = 1 if 0.8 <= ratio <= 1.4 else (2 if ratio > 1.4 else 0)
        target_tensor = torch.tensor([target_action], dtype=torch.long)

        # Quantum Model Forward & Backward Pass
        optimizer.zero_grad()
        logits = model(x_input)
        loss = criterion(logits, target_tensor)
        loss.backward()
        optimizer.step()

        # Analytics for UI and Terminal
        probs = torch.softmax(logits, dim=1).detach().squeeze().numpy()
        pred_action = actions[np.argmax(probs)]
        
        # Calculate Nash Equilibrium proxy (based on probability spread / mixed strategy)
        prob_std = np.std(probs)
        if prob_std < 0.1:
            nash_state = "Mixed Strategy (Balanced)"
        elif np.max(probs) > 0.8:
            nash_state = f"Pure Strategy (Dominated)"
        else:
            nash_state = "Transitional Fluctuations"

        # Update Graphs
        t_arr = np.array(time_buffer)
        line_r.set_data(t_arr, np.array(red_buf))
        line_g.set_data(t_arr, np.array(green_buf))
        line_b.set_data(t_arr, np.array(blue_buf))
        
        for ax in [ax_r, ax_g, ax_b]:
            ax.set_xlim(t_arr.min(), t_arr.max())

        for bar, prob in zip(bars, probs):
            bar.set_height(prob)

        # Update UI Panel Text
        ui_string = (
            f"SYSTEM METRICS\n"
            f"---------------------------\n"
            f"Learning Rate   : {LEARNING_RATE}\n"
            f"Circuit Balance : {loss.item():.4f} (Loss)\n"
            f"Prediction      : {pred_action}\n"
            f"Nash Eq State   : {nash_state}\n"
            f"Hardware Status : {'Active' if using_arduino else 'Synthetic'}"
        )
        info_text.set_text(ui_string)

        # Terminal Print Output (overwrites current line cleanly)
        sys.stdout.write(f"\r[Q-Engine] Loss: {loss.item():.4f} | Pred: {pred_action:12} | Nash Eq: {nash_state:25}")
        sys.stdout.flush()

        return [line_r, line_g, line_b, info_text] + list(bars)

    ani = FuncAnimation(fig, update, interval=30, blit=False, cache_frame_data=False)
    plt.show()
    print("\n[System] Shutdown initiated.")

if __name__ == "__main__":
    main()
