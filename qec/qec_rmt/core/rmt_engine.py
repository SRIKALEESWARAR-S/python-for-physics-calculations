"""
Random Matrix Theory Spectral Analysis Engine.

Implements:
- Hankel trajectory matrix construction from time series
- Wishart covariance eigenvalue extraction
- Legendre-polynomial spectral unfolding
- Brody chaoticity parameter estimation via Maximum Likelihood Estimation (MLE)

Classes:
    RMTAnalysisResult: Dataclass containing spectral analysis output
    RMTEngine: Main RMT computation engine
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize
from scipy.special import eval_legendre, gamma as gamma_fn

logger = logging.getLogger(__name__)


@dataclass
class RMTAnalysisResult:
    """Output of RMT spectral analysis for a single window."""

    window_idx: int
    eigenvalues: np.ndarray
    unfolded_spacings: np.ndarray
    brody_w: float
    brody_nll: Optional[float] = None  # Negative log-likelihood
    mean_spacing: float = 1.0
    validity: bool = True  # False if window is degenerate/invalid


class RMTEngine:
    """
    Random Matrix Theory spectral analysis engine.

    Processes time-series windows through Hankel embedding, Wishart eigenvalue
    extraction, Legendre unfolding, and Brody parameter MLE fitting.
    """

    def __init__(
        self,
        window_length: int = 200,
        window_step: int = 50,
        hankel_tau: int = 1,
        embedding_dim: Optional[int] = None,
        legendre_degree: int = 4,
        brody_bounds: Tuple[float, float] = (0.0, 1.0),
    ) -> None:
        """
        Initialize the RMT engine with windowing and unfolding parameters.

        Parameters
        ----------
        window_length : int
            Length of sliding windows, N.
        window_step : int
            Stride between window starts.
        hankel_tau : int
            Embedding lag in Hankel matrix.
        embedding_dim : Optional[int]
            Embedding dimension p (rows of Hankel). Defaults to N // 2.
        legendre_degree : int
            Degree K of Legendre expansion for unfolding.
        brody_bounds : Tuple[float, float]
            Bounds for Brody w parameter in MLE [0, 1].
        """
        self.window_length = window_length
        self.window_step = window_step
        self.hankel_tau = hankel_tau
        self.legendre_degree = legendre_degree
        self.brody_bounds = brody_bounds

        # Derived parameters
        self.p = embedding_dim if embedding_dim is not None else window_length // 2
        self.q = window_length - (self.p - 1) * hankel_tau

        if self.q < 2:
            raise ValueError(
                f"Hankel matrix would have < 2 columns: "
                f"N={window_length}, p={self.p}, tau={hankel_tau} -> q={self.q}"
            )

        logger.info(
            f"RMTEngine initialized: N={window_length}, p={self.p}, q={self.q}, "
            f"K={legendre_degree}"
        )

    def sliding_windows(self, series: np.ndarray) -> List[np.ndarray]:
        """
        Slice a 1-D standardized time series into overlapping windows.
        """
        series = np.asarray(series, dtype=np.float64).ravel()
        n_total = len(series)
        windows = []
        start = 0
        while start + self.window_length <= n_total:
            windows.append(series[start : start + self.window_length])
            start += self.window_step
        return windows

    def build_hankel(self, window: np.ndarray) -> np.ndarray:
        """
        Construct a p x q Hankel trajectory matrix.
        """
        p, q, tau = self.p, self.q, self.hankel_tau
        i_idx = np.arange(p).reshape(-1, 1)
        j_idx = np.arange(q).reshape(1, -1)
        idx = i_idx + j_idx * tau
        return window[idx]

    def wishart_eigenvalues(self, window: np.ndarray) -> np.ndarray:
        """
        Extract eigenvalues from symmetric Wishart matrix W = (1/p) H H^T.
        """
        H = self.build_hankel(window)
        W = (H @ H.T) / float(self.p)
        eigenvalues = eigh(W, eigvals_only=True)
        return np.sort(eigenvalues)

    def unfold_spectrum(self, eigenvalues: np.ndarray) -> np.ndarray:
        """
        Unfold eigenvalue spectrum using Legendre polynomial expansion.

        Maps eigenvalues to [-1, 1], fits cumulative spectral density via
        Legendre expansion, computes spacings, and normalizes to unit mean.
        """
        eigenvalues = np.sort(np.asarray(eigenvalues, dtype=np.float64))
        p = len(eigenvalues)
        if p < 3:
            return np.array([])

        lam_min, lam_max = eigenvalues.min(), eigenvalues.max()

        # Guard against degenerate or near-degenerate spectra (< 3 distinct eigenvalues)
        unique_vals = np.unique(np.round(eigenvalues, decimals=8))
        if np.isclose(lam_max, lam_min, atol=1e-8) or len(unique_vals) < 3:
            logger.warning(
                "Eigenvalue spectrum is degenerate or has insufficient unique values. "
                "Unfolding ill-defined."
            )
            return np.array([])

        # Map to [-1, 1]
        x = 2.0 * (eigenvalues - lam_min) / (lam_max - lam_min) - 1.0

        # Legendre design matrix Φ[i, n] = P_n(x_i)
        degrees = np.arange(self.legendre_degree + 1)
        Phi = np.vstack([eval_legendre(n, x) for n in degrees]).T  # (p, K+1)

        # Raw staircase counting function
        staircase = np.arange(1, p + 1, dtype=np.float64)

        # Least-squares fit: Φ a ≈ staircase
        try:
            coeffs, *_ = np.linalg.lstsq(Phi, staircase, rcond=None)
        except Exception as exc:
            logger.error(f"Least-squares fit failed: {exc}")
            return np.array([])

        # Smooth cumulative spectral density
        n_bar = Phi @ coeffs
        n_bar = np.maximum.accumulate(n_bar)

        # Spacings and normalization
        spacings = np.diff(n_bar)
        spacings = spacings[spacings > 0]
        if spacings.size == 0:
            return np.array([])

        mean_spacing = spacings.mean()
        if mean_spacing <= 1e-12:
            return np.array([])
        return spacings / mean_spacing

    @staticmethod
    def brody_pdf(s: np.ndarray, w: float) -> np.ndarray:
        """
        Brody distribution probability density function.
        """
        s = np.asarray(s, dtype=np.float64)
        s_safe = np.clip(s, 1e-12, None)
        try:
            c_w = gamma_fn((w + 2.0) / (w + 1.0)) ** (1.0 + w)
            return (
                c_w
                * (1.0 + w)
                * np.power(s_safe, w)
                * np.exp(-c_w * np.power(s_safe, 1.0 + w))
            )
        except Exception as exc:
            logger.error(f"Brody PDF evaluation failed at w={w}: {exc}")
            return np.zeros_like(s)

    def brody_mle(self, spacings: np.ndarray) -> Tuple[float, Optional[float]]:
        """
        Estimate Brody parameter w via unbinned Maximum Likelihood Estimation.
        """
        spacings = np.asarray(spacings, dtype=np.float64).ravel()
        spacings = spacings[np.isfinite(spacings) & (spacings > 0)]

        if spacings.size < 5:
            logger.warning(f"Too few valid spacings ({spacings.size}) for MLE.")
            return float("nan"), None

        def neg_log_likelihood(w: float) -> float:
            w = float(np.clip(w, self.brody_bounds[0], self.brody_bounds[1]))
            pdf_vals = self.brody_pdf(spacings, w)
            valid = pdf_vals > 1e-16
            if not valid.any():
                return 1e10
            return -np.sum(np.log(pdf_vals[valid]))

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = minimize(
                    neg_log_likelihood,
                    x0=[0.5],
                    bounds=[self.brody_bounds],
                    method="L-BFGS-B",
                    options={"maxiter": 5000},
                )

            if result.success or result.fun < 1e10:
                w_fit = float(np.clip(result.x[0], *self.brody_bounds))
                nll = float(result.fun)
                logger.debug(f"Brody MLE converged: w={w_fit:.4f}, NLL={nll:.4f}")
                return w_fit, nll
            else:
                logger.warning("Brody MLE optimization failed to converge.")
                return float("nan"), None
        except Exception as exc:
            logger.error(f"Brody MLE exception: {exc}")
            return float("nan"), None

    def process_window(
        self, window: np.ndarray, window_idx: int = 0
    ) -> RMTAnalysisResult:
        """
        Process a single time-series window through the full RMT pipeline.
        """
        window = np.asarray(window, dtype=np.float64).ravel()

        try:
            eigenvalues = self.wishart_eigenvalues(window)
        except Exception as exc:
            logger.error(f"Eigenvalue extraction failed for window {window_idx}: {exc}")
            return RMTAnalysisResult(
                window_idx=window_idx,
                eigenvalues=np.array([]),
                unfolded_spacings=np.array([]),
                brody_w=float("nan"),
                validity=False,
            )

        try:
            spacings = self.unfold_spectrum(eigenvalues)
        except Exception as exc:
            logger.error(f"Spectral unfolding failed for window {window_idx}: {exc}")
            return RMTAnalysisResult(
                window_idx=window_idx,
                eigenvalues=eigenvalues,
                unfolded_spacings=np.array([]),
                brody_w=float("nan"),
                validity=False,
            )

        w_fit, nll = self.brody_mle(spacings)
        mean_spacing = spacings.mean() if spacings.size > 0 else np.nan

        return RMTAnalysisResult(
            window_idx=window_idx,
            eigenvalues=eigenvalues,
            unfolded_spacings=spacings,
            brody_w=w_fit,
            brody_nll=nll,
            mean_spacing=mean_spacing,
            validity=np.isfinite(w_fit),
        )

    def process_series(
        self, series: np.ndarray, show_progress: bool = False
    ) -> List[RMTAnalysisResult]:
        """
        Process a full time series across all windows.
        """
        windows = self.sliding_windows(series)
        n_windows = len(windows)
        logger.info(f"Processing {n_windows} windows...")

        results = []
        for idx, window in enumerate(windows):
            if show_progress and (idx % max(1, n_windows // 10)) == 0:
                logger.info(f"  Progress: {100*idx/n_windows:.0f}%")
            result = self.process_window(window, window_idx=idx)
            results.append(result)

        n_valid = sum(1 for r in results if r.validity)
        logger.info(
            f"Completed: {n_windows} windows processed, {n_valid} valid RMT estimates."
        )
        return results
