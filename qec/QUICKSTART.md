# QEC-RMT-Studio: Quick Start Guide

**Get up and running in 5 minutes**

---

## Step 1: Extract and Install

```bash
# Extract the archive
tar -xzf qec_rmt_studio_complete.tar.gz
cd qec_rmt_studio

# Install the package with all dependencies
pip install -e ".[dev]"

# Optional: Install circuit simulation backend (stim + pymatching)
pip install -e ".[stim]"
```

**Verify Installation:**
```bash
python -c "from qec_rmt.core import DataSanitizer, RMTEngine, QECEngine; print('✓ All modules imported successfully')"
```

---

## Step 2: Launch the GUI

```bash
qec-rmt-studio
```

This opens an interactive PyQt6 dashboard with three tabs:

### **Tab 1: Telemetry & Ingestion**
- Click "Load CSV" to open your sensor data file
- View data health report (NaN, Inf, frozen sensors)
- See raw signal preview

### **Tab 2: RMT Spectral Analysis**
- Adjust window length and Legendre degree
- Click "Run RMT Analysis"
- View eigenvalue histogram and spacing distribution
- Check Brody fit statistics

### **Tab 3: QEC Threshold & Error Mapping**
- Use interactive sliders to adjust:
  - Code distance `d`
  - Threshold `p_th`
  - Prefactor `C`
- Watch `E_L(w)` and `p_phys(w)` curves update in real-time

---

## Step 3: Run Tests

```bash
# Full test suite with coverage
pytest tests/ -v --cov=qec_rmt --cov-report=term-missing

# Specific test category
pytest tests/test_pipeline.py::TestRMTEngine -v

# Single test
pytest tests/test_pipeline.py::TestDataSanitizer::test_sanitize_clean_data -v
```

---

## Step 4: Use from Python

```python
import numpy as np
from qec_rmt.core import DataSanitizer, RMTEngine, QECEngine

# 1. Load and sanitize your data
sanitizer = DataSanitizer()
your_data = np.random.randn(2000)
arr_clean, health = sanitizer.sanitize_array(your_data)
print(health.summary())

# 2. Extract environmental chaoticity
rmt_engine = RMTEngine(window_length=200)
results = rmt_engine.process_series(arr_clean)

# 3. Map to quantum error rates
qec_engine = QECEngine(d=3)
for result in results:
    if result.validity:
        w = result.brody_w
        qec_output = qec_engine.compute(w, use_stim=False)
        print(f"w={w:.3f} → E_L={qec_output.E_L:.6e}")
```

---

## Common Tasks

### Load Your Arduino CSV and Analyze

```python
import pandas as pd
from qec_rmt.core import DataSanitizer, RMTEngine, QECEngine

# Load CSV
df = pd.read_csv("sensor_readings.csv")

# Sanitize
sanitizer = DataSanitizer()
df_clean, health = sanitizer.sanitize_dataframe(df)
print(f"Data health: {health.summary()}")

# Process each sensor channel
rmt = RMTEngine()
qec = QECEngine(d=3)

for col in ["ldr", "distance_cm", "temperature_c", "humidity_pct"]:
    signal = df_clean[col].dropna().values
    results = rmt.process_series(signal)
    
    for r in results:
        if r.validity:
            el = qec.compute(r.brody_w).E_L
            print(f"{col}: w={r.brody_w:.3f}, E_L={el:.6e}")
```

### Generate Figures for Publication

```python
import matplotlib.pyplot as plt
import numpy as np

# Extract data from RMT results
spacings = results[0].unfolded_spacings  # First window
w_vals = np.array([r.brody_w for r in results if r.validity])
e_l_vals = np.array([qec.compute(w).E_L for w in w_vals])

# Plot 1: Spacing distribution
fig, ax = plt.subplots()
ax.hist(spacings, bins=30, density=True)
ax.set_xlabel("Normalized spacing s")
ax.set_ylabel("P(s)")
ax.set_title("Nearest-Neighbor Spacing Distribution")
plt.savefig("brody_fit.pdf")

# Plot 2: Correlation
fig, ax = plt.subplots()
ax.scatter(w_vals, e_l_vals)
ax.set_xlabel("Brody parameter w")
ax.set_ylabel("Logical error rate E_L")
ax.set_yscale("log")
ax.set_title("Environmental Chaoticity vs. QEC Performance")
plt.savefig("w_vs_el.pdf")

plt.show()
```

### Adjust QEC Parameters Interactively

```python
qec = QECEngine()

# Change code distance
qec.set_parameters(d=5)

# Compute E_L for various w values
w_array = np.linspace(0, 1, 100)
results = qec.compute_batch(w_array, use_stim=False)

# Extract and plot
e_l_vals = np.array([r.E_L for r in results])

import matplotlib.pyplot as plt
plt.semilogy(w_array, e_l_vals)
plt.xlabel("Brody parameter w")
plt.ylabel("Logical error rate E_L")
plt.show()
```

---

## Troubleshooting

### "No module named PyQt6"
```bash
pip install PyQt6 pyqtgraph
```

### "stim/pymatching not available"
This is fine! The pipeline falls back to analytical scaling laws automatically.
```bash
pip install stim pymatching  # Optional, for circuit simulation
```

### "CSV won't load"
Check that your CSV has numeric columns. The sanitizer expects:
- Numeric columns (float/int)
- Optional "timestamp" column
- No specific column name requirements (will detect all numeric)

### "Brody fit returns NaN"
This can happen if:
- The signal is nearly constant (zero variance)
- There are too many NaNs (>10% of data)
- The window length is too short (N < 50)

Check `health.summary()` to diagnose data quality.

---

## Architecture Overview

```
Sensor Data (CSV/Arduino)
         ↓
[DataSanitizer] ← Removes NaNs, Infs, frozen regions
         ↓
[RMTEngine] ← Hankel embedding → eigenvalues → unfolding → Brody fit
         ↓
    w_estimated (0.0 to 1.0)
         ↓
[QECEngine] ← Physical noise mapping → logical error rate
         ↓
    E_L (logical failure rate)
```

---

## File Organization

```
qec_rmt_studio/
├── qec_rmt/
│   ├── core/
│   │   ├── sanitizer.py      ← Data cleaning
│   │   ├── rmt_engine.py     ← Spectral analysis
│   │   └── qec_engine.py     ← Error rate mapping
│   └── gui/
│       └── app.py            ← PyQt6 dashboard
├── tests/
│   └── test_pipeline.py      ← 34 tests, 90% coverage
├── pyproject.toml            ← Dependencies & config
└── README.md                 ← Full documentation
```

---

## Key Formulas (Just the Important Ones!)

**Brody Parameter:**
- Characterizes signal regularity (w=0) vs. chaos (w=1)
- Extracted from nearest-neighbor eigenvalue spacings

**Physical Fault Probability:**
$$p_{\text{phys}}(w) = p_0(1 + \alpha w^\beta) = 0.002 \times (1 + 1.5 w^2)$$

**Logical Error Rate (Surface Code):**
$$E_L(p_{\text{phys}}) \approx C \left(\frac{p_{\text{phys}}}{p_{\text{th}}}\right)^{(d+1)/2}$$

where:
- d = code distance (default 3)
- p_th = threshold ≈ 0.011
- C = prefactor ≈ 0.1

---

## Next Steps

1. **Explore the GUI** — Load your Arduino CSV and visualize data quality
2. **Run the Test Suite** — Verify everything works: `pytest tests/ -v`
3. **Try the Python API** — Automate analysis for multiple datasets
4. **Read the README** — Full API reference and mathematical details

---

## Getting Help

- **README.md** — Complete user guide
- **Code docstrings** — Detailed documentation for each class/method
- **test_pipeline.py** — Working examples for every major feature
- **PROJECT_INDEX.md** — Detailed architecture and file manifest

---

**Ready to analyze your environmental sensor data?** 🚀

Start with: `qec-rmt-studio` or `python -c "from qec_rmt.core import *; print('OK')"`
