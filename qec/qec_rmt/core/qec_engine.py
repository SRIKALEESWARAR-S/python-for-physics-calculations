"""
Quantum Error Correction Noise Mapping Engine.

Maps environmental chaoticity (Brody w) to physical Pauli error probabilities
and surface code logical failure rates via standard QEC scaling relations and
optional circuit-level simulation (stim + pymatching).

Classes:
    PauliChannel: Depolarizing channel descriptor
    QECNoiseResult: Output of QEC analysis
    QECEngine: Main QEC computation engine
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PauliChannel:
    """Single-qubit depolarizing (Pauli) channel descriptor."""

    p_phys: float  # Total physical error probability
    p_x: float  # X error probability
    p_y: float  # Y error probability
    p_z: float  # Z error probability
    p_identity: float = 0.0  # Idle (no-error) probability, computed automatically

    def __post_init__(self) -> None:
        """Compute identity probability from component probabilities."""
        self.p_identity = max(0.0, 1.0 - self.p_phys)
        if self.p_identity < 0:
            logger.warning(
                f"p_phys={self.p_phys} > 1.0; clamping to valid range [0,1]."
            )
            self.p_phys = 1.0
            self.p_identity = 0.0


@dataclass
class QECNoiseResult:
    """Output of QEC noise analysis."""

    w: float  # Brody chaoticity parameter
    p_phys: float  # Physical fault probability
    p_x: float  # X component
    p_y: float  # Y component
    p_z: float  # Z component
    E_L: float  # Logical error rate
    method: str  # "analytical" or "stim+pymatching"


class QECEngine:
    """
    Quantum Error Correction noise mapping engine.

    Converts environmental chaoticity (Brody w) to physical Pauli error rates
    and computes surface code logical failure rates.
    """

    def __init__(
        self,
        p0: float = 0.002,
        alpha: float = 1.5,
        beta: float = 2.0,
        d: int = 3,
        p_th: float = 0.011,
        C: float = 0.1,
    ) -> None:
        """
        Initialize QEC engine with noise-mapping and surface-code parameters.

        Parameters
        ----------
        p0 : float
            Baseline physical fault probability (w=0).
        alpha : float
            Scaling coefficient for chaoticity-driven noise enhancement.
        beta : float
            Power-law exponent for chaoticity-driven noise enhancement.
        d : int
            Surface code distance.
        p_th : float
            Surface code error threshold.
        C : float
            Prefactor in below-threshold scaling relation for E_L.
        """
        self.p0 = p0
        self.alpha = alpha
        self.beta = beta
        self.d = d
        self.p_th = p_th
        self.C = C

        # Check for stim/pymatching availability
        self._stim_available = self._check_stim_pymatching()
        if not self._stim_available:
            logger.info("stim/pymatching not available; using analytical scaling only.")

        logger.info(
            f"QECEngine initialized: p0={p0}, α={alpha}, β={beta}, "
            f"d={d}, p_th={p_th}, C={C}, stim_available={self._stim_available}"
        )

    @staticmethod
    def _check_stim_pymatching() -> bool:
        """Check whether stim and pymatching are installed."""
        try:
            import stim  # noqa: F401
            import pymatching  # noqa: F401
            return True
        except ImportError:
            return False

    def w_to_p_phys(self, w: float) -> float:
        """
        Map Brody chaoticity parameter to physical fault probability.

        p_phys(w) = p0 * (1 + α * w^β)

        Parameters
        ----------
        w : float
            Brody parameter ∈ [0, 1]. NaN-safe.

        Returns
        -------
        float
            Physical fault probability, or np.nan if w is NaN.
        """
        if w is None or (isinstance(w, float) and np.isnan(w)):
            return float("nan")

        w_clipped = float(np.clip(w, 0.0, 1.0))
        return self.p0 * (1.0 + self.alpha * (w_clipped ** self.beta))

    def build_pauli_channel(self, p_phys: float) -> PauliChannel:
        """
        Build a symmetric depolarizing Pauli channel from fault probability.

        E(ρ) = (1 - p_phys)ρ + (p_x/3)XρX + (p_y/3)YρY + (p_z/3)ZρZ
        with p_x = p_y = p_z = p_phys (symmetric decomposition).

        Parameters
        ----------
        p_phys : float
            Total physical fault probability.

        Returns
        -------
        PauliChannel
            Pauli channel descriptor.
        """
        if np.isnan(p_phys):
            return PauliChannel(p_phys=float("nan"), p_x=float("nan"),
                               p_y=float("nan"), p_z=float("nan"))

        p_each = p_phys / 3.0
        return PauliChannel(p_phys=p_phys, p_x=p_each, p_y=p_each, p_z=p_each)

    def logical_error_rate_analytical(self, p_phys: float) -> float:
        """
        Estimate logical error rate via analytical below-threshold scaling.

        E_L ≈ C * (p_phys / p_th)^((d+1)/2)

        Parameters
        ----------
        p_phys : float
            Physical fault probability.

        Returns
        -------
        float
            Estimated logical error rate E_L.
        """
        if np.isnan(p_phys):
            return float("nan")

        exponent = (self.d + 1) / 2.0
        return self.C * (p_phys / self.p_th) ** exponent

    def logical_error_rate_stim(
        self, p_phys: float, num_shots: int = 1000
    ) -> Optional[float]:
        """
        Estimate logical error rate via stim + pymatching circuit simulation.

        Simulates a rotated surface code with circuit-level noise at rate p_phys
        and uses minimum-weight perfect matching (MWPM) decoding to estimate
        the logical failure rate.

        Parameters
        ----------
        p_phys : float
            Physical fault probability.
        num_shots : int
            Number of Monte Carlo shots to simulate.

        Returns
        -------
        Optional[float]
            Simulated logical error rate, or None if unavailable.
        """
        if not self._stim_available or np.isnan(p_phys):
            return None

        try:
            import stim
            import pymatching

            # Generate a rotated surface code circuit
            circuit = stim.Circuit.generated(
                "surface_code:rotated_memory_z",
                distance=self.d,
                rounds=self.d,
                after_clifford_depolarization=p_phys,
                before_round_data_depolarization=p_phys,
                before_measure_flip_probability=p_phys,
            )

            # Sample detection events and observable flips
            sampler = circuit.compile_detector_sampler()
            detection_events, observable_flips = sampler.sample(
                shots=num_shots, separate_observables=True
            )

            # Decode with minimum-weight perfect matching
            matcher = pymatching.Matching.from_detector_error_model(
                circuit.detector_error_model(decompose_errors=True)
            )
            predictions = matcher.decode_batch(detection_events)

            # Count logical failures
            n_errors = int(np.sum(np.any(predictions != observable_flips, axis=1)))
            return n_errors / float(num_shots)

        except Exception as exc:
            logger.warning(
                f"stim/pymatching simulation failed, falling back to analytical: {exc}"
            )
            return None

    def compute(
        self, w: float, use_stim: bool = True
    ) -> QECNoiseResult:
        """
        Full pipeline: w → p_phys → Pauli channel → E_L.

        Parameters
        ----------
        w : float
            Brody chaoticity parameter.
        use_stim : bool
            If True and stim/pymatching available, use circuit simulation.
            Otherwise use analytical scaling.

        Returns
        -------
        QECNoiseResult
            Complete QEC noise analysis.
        """
        p_phys = self.w_to_p_phys(w)
        channel = self.build_pauli_channel(p_phys)

        # Try circuit simulation first if requested
        e_l_stim = None
        if use_stim and self._stim_available:
            e_l_stim = self.logical_error_rate_stim(p_phys)

        # Fall back to or use analytical scaling
        if e_l_stim is not None:
            e_l = e_l_stim
            method = "stim+pymatching"
        else:
            e_l = self.logical_error_rate_analytical(p_phys)
            method = "analytical"

        return QECNoiseResult(
            w=w,
            p_phys=p_phys,
            p_x=channel.p_x,
            p_y=channel.p_y,
            p_z=channel.p_z,
            E_L=e_l,
            method=method,
        )

    def compute_batch(
        self, w_array: np.ndarray, use_stim: bool = True
    ) -> list[QECNoiseResult]:
        """
        Compute QEC metrics for an array of Brody parameters.

        Parameters
        ----------
        w_array : np.ndarray
            Array of Brody parameters.
        use_stim : bool
            If True and available, use circuit simulation.

        Returns
        -------
        list[QECNoiseResult]
            QEC results for each input w.
        """
        results = []
        for w in np.asarray(w_array).ravel():
            results.append(self.compute(float(w), use_stim=use_stim))
        return results

    def get_parameters_dict(self) -> Dict[str, float]:
        """Return a dictionary of all QEC engine parameters."""
        return {
            "p0": self.p0,
            "alpha": self.alpha,
            "beta": self.beta,
            "d": self.d,
            "p_th": self.p_th,
            "C": self.C,
        }

    def set_parameters(self, **kwargs: float) -> None:
        """
        Update QEC engine parameters.

        Valid keys: p0, alpha, beta, d, p_th, C
        """
        valid_keys = {"p0", "alpha", "beta", "d", "p_th", "C"}
        for key, value in kwargs.items():
            if key not in valid_keys:
                logger.warning(f"Unknown parameter '{key}'; ignoring.")
                continue
            setattr(self, key, float(value))
            logger.info(f"Set {key} = {value}")
