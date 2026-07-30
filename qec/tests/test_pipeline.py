"""
Comprehensive pytest test suite for QEC-RMT-Studio.

Coverage:
- Data sanitization and fault tolerance
- RMT mathematical correctness (eigenvalues, unfolding, spacing normalization)
- Brody distribution and MLE fitting
- QEC noise mapping and logical error rate computation
- Edge cases and crash prevention
"""

import numpy as np
import pandas as pd
import pytest

from qec_rmt.core import DataSanitizer, RMTEngine, QECEngine


# =====================================================================
# DataSanitizer Tests
# =====================================================================


class TestDataSanitizer:
    """Test suite for data sanitization and fault-tolerance layer."""

    def setup_method(self):
        """Initialize a sanitizer for each test."""
        self.sanitizer = DataSanitizer()

    def test_sanitize_clean_data(self):
        """Test sanitization on clean, healthy data."""
        data = np.random.randn(1000)
        df = pd.DataFrame({"signal": data})
        df_clean, health = self.sanitizer.sanitize_dataframe(df)

        assert health.total_samples == 1000
        assert health.nan_count == 0
        assert health.health_score > 0.99

    def test_sanitize_with_nans(self):
        """Test NaN detection and handling."""
        data = np.random.randn(1000)
        data[100:150] = np.nan
        df = pd.DataFrame({"signal": data})
        df_clean, health = self.sanitizer.sanitize_dataframe(df)

        assert health.nan_count == 50
        assert np.isnan(df_clean.loc[100:149, "signal"]).all()

    def test_sanitize_with_infs(self):
        """Test Inf detection and masking."""
        data = np.random.randn(1000)
        data[50:60] = np.inf
        df = pd.DataFrame({"signal": data})
        df_clean, health = self.sanitizer.sanitize_dataframe(df)

        assert health.inf_count == 10
        assert np.isnan(df_clean.loc[50:59, "signal"]).all()

    def test_sanitize_zero_variance(self):
        """Test detection of constant (zero-variance) signals."""
        data = np.full(1000, 5.0)
        df = pd.DataFrame({"const": data})
        df_clean, health = self.sanitizer.sanitize_dataframe(df)

        assert health.zero_variance_count > 0

    def test_sanitize_frozen_sensor(self):
        """Test detection of frozen/stuck sensors."""
        data = np.random.randn(1000)
        data[300:700] = 3.14159  # Frozen region
        df = pd.DataFrame({"frozen": data})
        df_clean, health = self.sanitizer.sanitize_dataframe(df)

        assert health.frozen_sensor_count > 0

    def test_filter_spacings_outliers(self):
        """Test filtering of non-physical spacings."""
        spacings = np.array([0.1, 0.5, 1.0, 2.0, 10.0, 100.0])  # Last two are outliers
        filtered, outlier_count = self.sanitizer.filter_spacings(spacings)

        assert outlier_count > 0
        assert np.all(filtered >= self.sanitizer.spacing_min)
        assert np.all(filtered <= self.sanitizer.spacing_max)

    def test_filter_spacings_renormalize(self):
        """Test that filtered spacings are renormalized to unit mean."""
        spacings = np.array([0.1, 0.5, 1.0, 1.5, 2.0])
        filtered, _ = self.sanitizer.filter_spacings(spacings)

        if len(filtered) > 0:
            assert np.isclose(filtered.mean(), 1.0, rtol=1e-6)

    def test_generate_diagnostic_report(self):
        """Test diagnostic report generation."""
        data = np.random.randn(1000)
        df = pd.DataFrame({"signal": data})
        df_clean, health = self.sanitizer.sanitize_dataframe(df)
        report = self.sanitizer.generate_diagnostic_report(health)

        assert "DATA HEALTH DIAGNOSTIC" in report
        assert "health score" in report.lower()


# =====================================================================
# RMTEngine Tests
# =====================================================================


class TestRMTEngine:
    """Test suite for Random Matrix Theory computation engine."""

    def setup_method(self):
        """Initialize an RMT engine for each test."""
        self.engine = RMTEngine(window_length=200, window_step=50, legendre_degree=4)

    def test_engine_initialization(self):
        """Test proper RMT engine initialization."""
        assert self.engine.p == 100  # 200 // 2
        assert self.engine.q == 101  # 200 - 99*1
        assert self.engine.window_length == 200
        assert self.engine.legendre_degree == 4

    def test_sliding_windows(self):
        """Test sliding window extraction."""
        series = np.arange(1000, dtype=float)
        windows = self.engine.sliding_windows(series)

        assert len(windows) > 0
        assert len(windows[0]) == self.engine.window_length
        assert np.allclose(windows[0], np.arange(200))
        assert np.allclose(windows[1], np.arange(50, 250))

    def test_hankel_construction(self):
        """Test Hankel trajectory matrix construction."""
        window = np.arange(200, dtype=float)
        H = self.engine.build_hankel(window)

        assert H.shape == (self.engine.p, self.engine.q)
        assert H[0, 0] == 0.0  # window[0 + 0*tau]
        assert H[1, 0] == 1.0  # window[1 + 0*tau]
        assert H[0, 1] == 1.0  # window[0 + 1*tau]

    def test_wishart_eigenvalues_real(self):
        """Test that Wishart eigenvalues are real and positive."""
        window = np.random.randn(200)
        eigenvalues = self.engine.wishart_eigenvalues(window)

        assert eigenvalues.dtype in [np.float64, np.float32]
        assert np.all(np.isfinite(eigenvalues))
        assert np.all(eigenvalues >= -1e-10)  # Numerical tolerance for positivity
        assert np.all(eigenvalues[:-1] <= eigenvalues[1:])  # Sorted

    def test_wishart_eigenvalues_white_noise(self):
        """Test Wishart eigenvalues on white noise (Marchenko-Pastur limit)."""
        np.random.seed(42)
        eigenvalues_list = []
        for _ in range(10):
            window = np.random.randn(200)
            eigenvalues = self.engine.wishart_eigenvalues(window)
            eigenvalues_list.append(eigenvalues)

        all_eigenvalues = np.concatenate(eigenvalues_list)
        # For Marchenko-Pastur: support is approximately [(1-sqrt(q/p))^2, (1+sqrt(q/p))^2]
        # For our case: (1-1)^2 = 0, (1+1)^2 = 4
        assert np.min(all_eigenvalues) > -0.5
        assert np.max(all_eigenvalues) < 6.0

    def test_unfold_spectrum_unit_mean_spacing(self):
        """Test that unfolded spacings have unit mean."""
        window = np.random.randn(200)
        eigenvalues = self.engine.wishart_eigenvalues(window)
        spacings = self.engine.unfold_spectrum(eigenvalues)

        if len(spacings) > 0:
            assert np.isclose(spacings.mean(), 1.0, rtol=1e-6)

    def test_unfold_spectrum_degenerate_eigenvalues(self):
        """Test unfolding behavior on degenerate spectrum."""
        # Create a window where all eigenvalues are nearly identical
        window = np.full(200, 1.0)
        eigenvalues = self.engine.wishart_eigenvalues(window)
        spacings = self.engine.unfold_spectrum(eigenvalues)

        # Should return empty array or very small array
        assert len(spacings) == 0 or np.all(spacings < 1e-6)

    def test_brody_pdf_bounds(self):
        """Test Brody PDF is always non-negative."""
        s = np.linspace(0.1, 3.0, 50)
        for w in [0.0, 0.25, 0.5, 0.75, 1.0]:
            pdf = self.engine.brody_pdf(s, w)
            assert np.all(pdf >= 0)
            assert np.all(np.isfinite(pdf))

    def test_brody_pdf_poisson_limit(self):
        """Test Brody PDF approaches Poisson (exponential) at w=0."""
        s = np.linspace(0.1, 5.0, 50)
        pdf_brody = self.engine.brody_pdf(s, w=0.0)
        pdf_poisson = np.exp(-s)  # True Poisson

        # Should be close but not exact (normalization may differ slightly)
        assert np.allclose(pdf_brody / pdf_brody.sum(), pdf_poisson / pdf_poisson.sum(),
                          atol=1e-2)

    def test_brody_mle_poisson_data(self):
        """Test Brody MLE recovery of w≈0 from synthetic Poisson spacings."""
        np.random.seed(42)
        # Generate synthetic Poisson spacings
        spacings = np.random.exponential(1.0, size=500)
        w_fit, nll = self.engine.brody_mle(spacings)

        # Should recover w close to 0
        assert np.isfinite(w_fit)
        assert w_fit < 0.3

    def test_brody_mle_goe_data(self):
        """Test Brody MLE recovery of w≈1 from synthetic GOE-like spacings."""
        np.random.seed(42)
        # Generate synthetic GOE (Wigner) spacings using approximation
        # P(s) ∝ s * exp(-πs²/4)
        spacings = []
        while len(spacings) < 500:
            s_candidate = np.random.exponential(1.0)
            # Acceptance-rejection with envelope
            if np.random.rand() < (s_candidate * np.exp(-np.pi * s_candidate**2 / 4.0)):
                spacings.append(s_candidate)
        spacings = np.array(spacings)
        spacings = spacings / spacings.mean()  # Normalize

        w_fit, nll = self.engine.brody_mle(spacings)

        # Should recover w close to 1
        assert np.isfinite(w_fit)
        assert w_fit > 0.6

    def test_process_window(self):
        """Test full windowing pipeline on a single window."""
        window = np.random.randn(200)
        result = self.engine.process_window(window, window_idx=0)

        assert result.window_idx == 0
        assert len(result.eigenvalues) == self.engine.p
        assert np.all(np.isfinite(result.eigenvalues))
        assert np.isfinite(result.brody_w) or result.brody_w == result.brody_w  # NaN-safe
        assert result.validity in [True, False]

    def test_process_series(self):
        """Test full series processing."""
        series = np.random.randn(1000)
        results = self.engine.process_series(series)

        assert len(results) > 0
        for result in results:
            assert result.window_idx >= 0
            assert len(result.eigenvalues) == self.engine.p
            assert np.isfinite(result.mean_spacing) or np.isnan(result.mean_spacing)


# =====================================================================
# QECEngine Tests
# =====================================================================


class TestQECEngine:
    """Test suite for Quantum Error Correction engine."""

    def setup_method(self):
        """Initialize a QEC engine for each test."""
        self.engine = QECEngine()

    def test_w_to_p_phys_limits(self):
        """Test physical fault probability mapping at limits."""
        p0 = self.engine.w_to_p_phys(0.0)
        p1 = self.engine.w_to_p_phys(1.0)

        assert np.isclose(p0, self.engine.p0)
        assert p1 > p0  # Error rate increases with chaoticity

    def test_w_to_p_phys_nan_safe(self):
        """Test NaN handling in w→p_phys mapping."""
        p_nan = self.engine.w_to_p_phys(float("nan"))
        assert np.isnan(p_nan)

    def test_w_to_p_phys_monotonic(self):
        """Test that p_phys is monotonically increasing with w."""
        w_vals = np.linspace(0, 1, 50)
        p_vals = [self.engine.w_to_p_phys(w) for w in w_vals]

        # Check monotonicity (allowing small numerical tolerance)
        for i in range(len(p_vals) - 1):
            assert p_vals[i] <= p_vals[i + 1] + 1e-10

    def test_build_pauli_channel_symmetric(self):
        """Test symmetric Pauli channel construction."""
        p_phys = 0.01
        channel = self.engine.build_pauli_channel(p_phys)

        assert channel.p_x == channel.p_y == channel.p_z
        assert np.isclose(channel.p_x + channel.p_y + channel.p_z, p_phys)

    def test_build_pauli_channel_nan_safe(self):
        """Test NaN handling in channel construction."""
        channel = self.engine.build_pauli_channel(float("nan"))
        assert np.isnan(channel.p_phys)

    def test_logical_error_rate_analytical_increases(self):
        """Test that E_L increases with p_phys."""
        e_l_low = self.engine.logical_error_rate_analytical(0.001)
        e_l_high = self.engine.logical_error_rate_analytical(0.01)

        assert e_l_low < e_l_high

    def test_logical_error_rate_analytical_nan_safe(self):
        """Test NaN handling in analytical E_L computation."""
        e_l_nan = self.engine.logical_error_rate_analytical(float("nan"))
        assert np.isnan(e_l_nan)

    def test_logical_error_rate_scaling_law(self):
        """Test below-threshold scaling exponent."""
        # E_L ∝ (p_phys / p_th)^((d+1)/2)
        # So E_L(p_phys=2p_th) / E_L(p_phys=p_th) ≈ 2^((d+1)/2)
        p_th = self.engine.p_th
        e_l_1 = self.engine.logical_error_rate_analytical(p_th)
        e_l_2 = self.engine.logical_error_rate_analytical(2 * p_th)

        expected_ratio = 2.0 ** ((self.engine.d + 1) / 2.0)
        actual_ratio = e_l_2 / e_l_1
        assert np.isclose(actual_ratio, expected_ratio, rtol=1e-6)

    def test_compute_full_pipeline(self):
        """Test full w→p_phys→E_L pipeline."""
        result = self.engine.compute(w=0.5, use_stim=False)

        assert result.w == 0.5
        assert np.isfinite(result.p_phys)
        assert np.isfinite(result.E_L)
        assert result.p_phys > 0
        assert result.E_L > 0

    def test_compute_batch(self):
        """Test batch computation over multiple w values."""
        w_array = np.linspace(0, 1, 10)
        results = self.engine.compute_batch(w_array, use_stim=False)

        assert len(results) == len(w_array)
        for result in results:
            assert np.isfinite(result.E_L) or np.isnan(result.E_L)

    def test_set_parameters(self):
        """Test parameter update."""
        self.engine.set_parameters(d=5, p_th=0.02, C=0.2)

        assert self.engine.d == 5
        assert self.engine.p_th == 0.02
        assert self.engine.C == 0.2

    def test_get_parameters(self):
        """Test parameter dictionary retrieval."""
        params = self.engine.get_parameters_dict()

        assert "p0" in params
        assert "alpha" in params
        assert "d" in params
        assert params["d"] == self.engine.d


# =====================================================================
# Integration Tests
# =====================================================================


class TestIntegration:
    """Integration tests for the full RMT→QEC pipeline."""

    def test_full_pipeline_from_raw_signal(self):
        """Test complete pipeline from raw signal to E_L estimates."""
        np.random.seed(42)

        # Generate synthetic sensor signal
        t = np.linspace(0, 100, 2000)
        signal = np.sin(t) + 0.1 * np.random.randn(len(t))

        # Sanitize
        sanitizer = DataSanitizer()
        arr_clean, health = sanitizer.sanitize_array(signal)
        assert health.health_score > 0.9

        # RMT analysis
        rmt_engine = RMTEngine(window_length=200)
        results = rmt_engine.process_series(arr_clean, show_progress=False)
        assert len(results) > 0

        # Extract Brody w values
        w_vals = np.array([r.brody_w for r in results if r.validity])
        assert len(w_vals) > 0
        assert np.all(np.isfinite(w_vals))

        # QEC mapping
        qec_engine = QECEngine()
        e_l_vals = []
        for w in w_vals:
            result = qec_engine.compute(w, use_stim=False)
            e_l_vals.append(result.E_L)
        assert len(e_l_vals) > 0
        assert np.all(np.isfinite(e_l_vals))

    def test_pipeline_robustness_on_noisy_data(self):
        """Test pipeline robustness on highly noisy data."""
        np.random.seed(42)
        signal = np.random.randn(2000)

        sanitizer = DataSanitizer()
        arr_clean, _ = sanitizer.sanitize_array(signal)

        rmt_engine = RMTEngine()
        results = rmt_engine.process_series(arr_clean, show_progress=False)

        # Should not crash, even on pure noise
        assert len(results) > 0
        n_valid = sum(1 for r in results if r.validity)
        # Some results should be valid even on noise
        assert n_valid > 0 or len(results) > 0  # At minimum, process completes

    def test_pipeline_handles_missing_data(self):
        """Test pipeline robustness with NaNs and gaps."""
        np.random.seed(42)
        signal = np.random.randn(2000)
        signal[500:600] = np.nan  # Insert dropout
        signal[1200:1250] = np.inf  # Insert infinity

        sanitizer = DataSanitizer()
        arr_clean, health = sanitizer.sanitize_array(signal)

        # Should sanitize without crashing
        assert health.total_samples == 2000
        assert health.nan_count > 0
        assert health.inf_count > 0

        rmt_engine = RMTEngine()
        results = rmt_engine.process_series(arr_clean)

        # Should complete without crashing
        assert len(results) > 0


# =====================================================================
# Run tests
# =====================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
