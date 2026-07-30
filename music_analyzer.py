import numpy as np
import scipy.signal as signal
from scipy.spatial.distance import cosine
import scipy.linalg
import librosa
import matplotlib.pyplot as plt

def process_audio_to_qubit_states(file_path, frame_duration=5.0):
    """
    1. Audio -> Digital Signal (TimeSeries)
    2. Fourier Transform -> Frequency Spectrum
    3. Hankel Matrix -> State Space Representation
    4. Mapping to Qubit States (-1, 0, 1) & Noise Estimation
    """
    # 1. Load Audio File
    y, sr = librosa.load(file_path, sr=None)
    
    # 2. Fourier Transform (STFT for time-frequency analysis)
    n_fft = 2048
    hop_length = int(sr * 0.1) # 100ms hops
    stft = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    
    # Fundamental frequency / Pitch extraction
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length)
    f0 = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        f0.append(pitch if pitch > 0 else 0)
    f0 = np.array(f0)
    
    # Normalize pitch to range [-1, 1] for Spin State Representation
    if np.max(f0) > 0:
        norm_pitch = (f0 - np.mean(f0)) / (np.std(f0) + 1e-6)
        norm_pitch = np.clip(norm_pitch, -1.0, 1.0)
    else:
        norm_pitch = np.zeros_like(f0)

    # 3. Hankel Matrix Construction for Quantum/Matrix Representation
    N = len(norm_pitch)
    L = N // 2
    hankel_matrix = scipy.linalg.hankel(norm_pitch[:L], norm_pitch[L-1:])
    
    # SVD (Singular Value Decomposition) to get Eigen-values / Singular Values
    U, S, Vh = np.linalg.svd(hankel_matrix, full_matrices=False)
    
    # 4. Map to Discrete Qubit States: |1> (High), |0> (Mid/Neutral), |-1> (Low)
    qubit_states = np.zeros_like(norm_pitch)
    qubit_states[norm_pitch > 0.33] = 1.0     # |1> State
    qubit_states[norm_pitch < -0.33] = -1.0   # |-1> State
    # Remaining are 0.0 -> |0> State
    
    # Noise Estimation (High-frequency deviation / Spectral Flatness)
    flatness = librosa.feature.spectral_flatness(y=y, n_fft=n_fft, hop_length=hop_length)[0]
    
    times = np.linspace(0, len(y) / sr, len(qubit_states))
    return times, norm_pitch, qubit_states, flatness, S

def plot_comparative_qubit_graphs(orig_file, user_file):
    """
    Plotting Original vs User Sang Audio in Qubit / Spin Representation
    with 5-second precision markers & Noise Annotations.
    """
    print(f"Processing Original Audio: {orig_file} ...")
    t_orig, pitch_orig, q_orig, noise_orig, svd_orig = process_audio_to_qubit_states(orig_file)
    
    print(f"Processing Your Audio: {user_file} ...")
    t_user, pitch_user, q_user, noise_user, svd_user = process_audio_to_qubit_states(user_file)
    
    # Create Subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle('Quantum Frequency & Qubit Spin-State Audio Comparison', fontsize=14, fontweight='bold')
    
    # Graph 1: Original Audio Qubit Representation
    ax1.plot(t_orig, q_orig, color='blue', label='Original Qubit State (|1>, |0>, |-1>)', alpha=0.7)
    ax1.set_ylabel('Qubit State / Spin')
    ax1.set_yticks([-1, 0, 1])
    ax1.set_yticklabels(['|-1⟩ (Low)', '|0⟩ (Mid)', '|1⟩ (High)'])
    ax1.set_title('Original Reference Track')
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    # Highlight Noise regions in Original
    noise_indices_orig = np.where(noise_orig > 0.1)[0]
    if len(noise_indices_orig) > 0:
        ax1.scatter(t_orig[noise_indices_orig], q_orig[noise_indices_orig], color='red', s=10, label='High Noise Zone')
    ax1.legend(loc='upper right')
    
    # Graph 2: User Audio Qubit Representation
    ax2.plot(t_user, q_user, color='green', label='Your Qubit State (|1>, |0>, |-1>)', alpha=0.7)
    ax2.set_xlabel('Time (Seconds) [5s Precision Grid]')
    ax2.set_ylabel('Qubit State / Spin')
    ax2.set_yticks([-1, 0, 1])
    ax2.set_yticklabels(['|-1⟩ (Low)', '|0⟩ (Mid)', '|1⟩ (High)'])
    ax2.set_title('Your Vocal Pitch & Qubit Match')
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    # 5-second Grid Precision
    max_time = max(t_orig[-1], t_user[-1])
    plt.xticks(np.arange(0, max_time + 5, 5.0))
    
    # Annotate Noise / Pitch Mismatch
    q_user_interp = np.interp(t_orig, t_user, q_user)
    diff = np.abs(q_orig - q_user_interp)
    mismatch_times = t_orig[diff > 1.0]
    
    for m_time in mismatch_times[::10]: # Annotate sample points
        ax2.annotate('Mismatch', xy=(m_time, 0), xytext=(m_time, 0.5),
                     arrowprops=dict(facecolor='orange', shrink=0.05, headwidth=4, width=1),
                     fontsize=8, color='darkred')
        
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Audio processing தொடங்குகிறது... தயவுசெய்து காத்திருக்கவும்.")
    
    original_track = 'orig.mp3' 
    user_track = 'spbv.mp3' 
    
    try:
        plot_comparative_qubit_graphs(original_track, user_track)
        print("வரைபடம் வெற்றிகரமாக உருவாக்கப்பட்டுவிட்டது!")
    except Exception as e:
        print(f"பிழை (Error): {e}")
