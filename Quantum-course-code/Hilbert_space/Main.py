import serial
import time
import numpy as np

# Update 'COM3' (Windows) or '/dev/ttyUSB0' / '/dev/ttyACM0' (Linux/Mac)
SERIAL_PORT = 'COM3'  
BAUD_RATE = 9600
THRESHOLD_CM = 30.0

def simulate_hilbert_space(distance_cm):
    """
    Models state evolution based on proximity:
    - > 30 cm: Isolated 2D Hilbert Space (Pure State, Purity = 1.0)
    - <= 30 cm: Augmented 4D Hilbert Space H_S (x) H_E (Decoherence, Purity < 1.0)
    """
    if distance_cm > THRESHOLD_CM:
        # Isolated System: |psi> = 1/sqrt(2) (|0> + |1>) in H_S (dim = 2)
        psi = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
        rho_s = np.outer(psi, psi.conj())
        purity = np.real(np.trace(rho_s @ rho_s))
        return {
            "status": "COHERENT (Isolated System)",
            "hilbert_dim": 2,
            "purity": round(purity, 4),
            "note": "H_S intact; negligible environmental coupling."
        }
    else:
        # Augmented Hilbert Space: H_S (x) H_E (dim = 4)
        # Coupling angle theta increases as distance approaches 0 cm
        coupling_strength = 1.0 - (max(distance_cm, 0.0) / THRESHOLD_CM)
        theta = coupling_strength * (np.pi / 2)

        # Entangled state: 1/sqrt(2) (|0>_S |e0>_E + |1>_S (cos(theta)|e0>_E + sin(theta)|e1>_E))
        psi_augmented = np.array([
            1/np.sqrt(2),                      # |00>
            0.0,                               # |01>
            (1/np.sqrt(2)) * np.cos(theta),    # |10>
            (1/np.sqrt(2)) * np.sin(theta)     # |11>
        ], dtype=complex)

        # Full density matrix in augmented space
        rho_total = np.outer(psi_augmented, psi_augmented.conj())

        # Partial trace over Environment (H_E) to get reduced density matrix rho_S
        rho_reshaped = rho_total.reshape(2, 2, 2, 2)
        rho_s = np.trace(rho_reshaped, axis1=1, axis2=3)

        # Purity Tr(rho_S^2): 1.0 = pure, 0.5 = maximally mixed (complete decoherence)
        purity = np.real(np.trace(rho_s @ rho_s))

        return {
            "status": "DECOHERENCE (Hilbert Space Augmented)",
            "hilbert_dim": 4,
            "purity": round(purity, 4),
            "note": f"Coupling: {coupling_strength*100:.1f}% | Tracing out H_E degrades coherence."
        }

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow Arduino auto-reset to finish
        print(f"Connected to {SERIAL_PORT}. Monitoring quantum-environmental boundary ({THRESHOLD_CM} cm)...\n")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if ',' in line:
                    try:
                        dist_str, _ = line.split(',')
                        distance = float(dist_str)
                        analysis = simulate_hilbert_space(distance)

                        print(
                            f"Dist: {distance:6.2f} cm | "
                            f"Dim(H): {analysis['hilbert_dim']} | "
                            f"Purity: {analysis['purity']:.4f} | "
                            f"{analysis['status']} -> {analysis['note']}"
                        )
                    except ValueError:
                        continue

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except KeyboardInterrupt:
        print("\nObservation terminated. Collapsing connection.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
  
