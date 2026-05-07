import sys
import numpy as np  
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter
import scipy.io.wavfile as wav
from scipy.signal import spectrogram as scipy_spectrogram

def load_wav(filepath: str):
    sample_rate,data = wav.read(filepath)
        # Convert to float in [-1, 1]
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    elif data.dtype == np.uint8:
        data = (data.astype(np.float32) - 128) / 128.0
    else:
        data = data.astype(np.float32)
 
    # Mix stereo → mono
    if data.ndim == 2:
        data = data.mean(axis=1)
 
    return sample_rate, data
# ─────────────────────────────────────────
# 2. FFT ANALYSIS
# ─────────────────────────────────────────
 
def compute_fft(signal, sample_rate):
    n = len(signal)
    # Apply Hann window to reduce spectral leakage
    window = np.hanning(n)
    windowed = signal * window
 
    fft_vals = np.fft.rfft(windowed)
    fft_freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
 
    magnitude = np.abs(fft_vals)
    magnitude_norm = magnitude / magnitude.max()           # normalised 0-1
    power_db = 20 * np.log10(magnitude + 1e-10)           # dB scale
 
    return fft_freqs, magnitude_norm, power_db
def top_frequencies(freqs, magnitude, n=10):
    """Return the n dominant frequency peaks."""
    # Simple peak picking: only keep local maxima
    from scipy.signal import find_peaks
    peaks, props = find_peaks(magnitude, height=0.05, distance=10)
    if len(peaks) == 0:
        # Fallback: just sort by magnitude
        idx = np.argsort(magnitude)[::-1][:n]
        return list(zip(freqs[idx], magnitude[idx]))
 
    # Sort peaks by magnitude descending
    peak_mags = magnitude[peaks]
    order = np.argsort(peak_mags)[::-1]
    top = [(freqs[peaks[i]], magnitude[peaks[i]]) for i in order[:n]]
    return top
 
 
# ─────────────────────────────────────────
# 3. PLOT
# ────────────────────────────────────────

def plot_analysis(filepath, sample_rate, signal):
    fft_freqs, magnitude_norm, power_db = compute_fft(signal, sample_rate)
    top = top_frequencies(fft_freqs, magnitude_norm, n=8)
 
    duration = len(signal) / sample_rate
    time_axis = np.linspace(0, duration, len(signal))
 
    # ── Spectrogram ──
    nperseg = min(1024, len(signal) // 8)
    f_spec, t_spec, Sxx = scipy_spectrogram(
        signal, fs=sample_rate, nperseg=nperseg, noverlap=nperseg // 2
    )
    Sxx_db = 10 * np.log10(Sxx + 1e-10)
 
    # ── Figure layout ──
    fig = plt.figure(figsize=(16, 14), facecolor="#0d1117")
    fig.suptitle(
        f"FFT Sound Wave Analysis  —  {filepath.split('/')[-1].split(chr(92))[-1]}\n"
        f"Sample rate: {sample_rate:,} Hz  |  Duration: {duration:.2f}s  |  Samples: {len(signal):,}",
        color="#e6edf3", fontsize=13, fontweight="bold", y=0.98
    )
 
    gs = gridspec.GridSpec(
        3, 2,
        figure=fig,
        hspace=0.48, wspace=0.35,
        top=0.93, bottom=0.07, left=0.08, right=0.95
    )
 
    ax_wave  = fig.add_subplot(gs[0, :])   # full-width waveform
    ax_fft   = fig.add_subplot(gs[1, 0])   # FFT magnitude
    ax_psd   = fig.add_subplot(gs[1, 1])   # Power (dB)
    ax_spec  = fig.add_subplot(gs[2, 0])   # Spectrogram
    ax_top   = fig.add_subplot(gs[2, 1])   # Top frequencies bar chart
 
    axes = [ax_wave, ax_fft, ax_psd, ax_spec, ax_top]
    for ax in axes:
        ax.set_facecolor("#161b22")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")
        ax.tick_params(colors="#8b949e", labelsize=8)
        ax.xaxis.label.set_color("#8b949e")
        ax.yaxis.label.set_color("#8b949e")
        ax.title.set_color("#e6edf3")
 
    CYAN   = "#58a6ff"
    GREEN  = "#3fb950"
    ORANGE = "#f78166"
    PURPLE = "#bc8cff"
 
    # ── (1) Waveform ──
    # Downsample for speed when signal is very long
    ds = max(1, len(signal) // 8000)
    ax_wave.plot(time_axis[::ds], signal[::ds], color=CYAN, lw=0.6, alpha=0.9)
    ax_wave.fill_between(time_axis[::ds], signal[::ds], alpha=0.15, color=CYAN)
    ax_wave.axhline(0, color="#30363d", lw=0.8, ls="--")
    ax_wave.set_title("Time-Domain Waveform", fontsize=10)
    ax_wave.set_xlabel("Time (s)")
    ax_wave.set_ylabel("Amplitude")
    ax_wave.set_xlim(0, duration)
    ax_wave.set_ylim(-1.05, 1.05)
 
    # ── (2) FFT Magnitude ──
    ax_fft.plot(fft_freqs, magnitude_norm, color=GREEN, lw=0.7)
    ax_fft.fill_between(fft_freqs, magnitude_norm, alpha=0.2, color=GREEN)
    for freq, mag in top[:3]:
        ax_fft.axvline(freq, color=ORANGE, lw=0.8, ls="--", alpha=0.7)
        ax_fft.text(freq, mag + 0.02, f"{freq:.0f}Hz", color=ORANGE,
                    fontsize=6.5, ha="center", va="bottom")
    ax_fft.set_title("FFT Magnitude Spectrum", fontsize=10)
    ax_fft.set_xlabel("Frequency (Hz)")
    ax_fft.set_ylabel("Normalised Magnitude")
    ax_fft.set_xlim(0, min(fft_freqs[-1], sample_rate / 2))
    ax_fft.set_ylim(0, 1.12)
    ax_fft.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
 
    # ── (3) Power Spectral Density ──
    ax_psd.plot(fft_freqs, power_db, color=PURPLE, lw=0.7)
    ax_psd.fill_between(fft_freqs, power_db, power_db.min(), alpha=0.15, color=PURPLE)
    ax_psd.set_title("Power Spectral Density (dB)", fontsize=10)
    ax_psd.set_xlabel("Frequency (Hz)")
    ax_psd.set_ylabel("Power (dB)")
    ax_psd.set_xlim(0, min(fft_freqs[-1], sample_rate / 2))
    ax_psd.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
 
    # ── (4) Spectrogram ──
    vmin = np.percentile(Sxx_db, 10)
    im = ax_spec.pcolormesh(t_spec, f_spec, Sxx_db,
                             shading="gouraud", cmap="inferno",
                             vmin=vmin, vmax=Sxx_db.max())
    cbar = fig.colorbar(im, ax=ax_spec, pad=0.02)
    cbar.ax.tick_params(colors="#8b949e", labelsize=7)
    cbar.set_label("Power (dB)", color="#8b949e", fontsize=8)
    ax_spec.set_title("Spectrogram (Time × Frequency)", fontsize=10)
    ax_spec.set_xlabel("Time (s)")
    ax_spec.set_ylabel("Frequency (Hz)")
    ax_spec.set_ylim(0, min(f_spec[-1], sample_rate / 2))
 
    # ── (5) Top dominant frequencies ──
    if top:
        top_f  = [f"{f:.1f}" for f, _ in top]
        top_m  = [m for _, m in top]
        colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(top)))
        bars = ax_top.barh(top_f[::-1], top_m[::-1], color=colors[::-1],
                           edgecolor="#30363d", height=0.65)
        for bar, mag in zip(bars, top_m[::-1]):
            ax_top.text(mag + 0.01, bar.get_y() + bar.get_height() / 2,
                        f"{mag:.3f}", va="center", color="#e6edf3", fontsize=7)
        ax_top.set_title("Top Dominant Frequencies", fontsize=10)
        ax_top.set_xlabel("Normalised Magnitude")
        ax_top.set_xlim(0, 1.15)
        ax_top.set_ylabel("Frequency (Hz)")
 
    plt.savefig("fft_analysis_output.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print("✅  Plot saved as  fft_analysis_output.png")
    plt.show()
 
 
# ─────────────────────────────────────────
# 4. ENTRY POINT
# ─────────────────────────────────────────
 
def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename(
                title="Select a WAV file",
                filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
            )
            root.destroy()
            if not filepath:
                print("No file selected. Exiting.")
                sys.exit(0)
        except Exception:
            print("Usage: python sound_wave_fft_analyzer.py <path_to_file.wav>")
            sys.exit(1)
 
    print(f"📂  Loading: {filepath}")
    sample_rate, signal = load_wav(filepath)
    print(f"   Sample rate : {sample_rate:,} Hz")
    print(f"   Samples     : {len(signal):,}")
    print(f"   Duration    : {len(signal)/sample_rate:.2f} s")
    print(f"   Amplitude ∈ [{signal.min():.3f}, {signal.max():.3f}]")
 
    plot_analysis(filepath, sample_rate, signal)
 
 
if __name__ == "__main__":
    main()
 
