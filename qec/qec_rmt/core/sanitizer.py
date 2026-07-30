"""
Data Sanitization and Fault Tolerance Layer.

Provides robust, zero-crash data ingestion with automatic detection and filtering
of hardware dropouts, NaNs, constant/zero-padded streams, and near-degenerate
sensor signals. All diagnostics are returned without raising unhandled exceptions.

Classes:
    HealthMetrics: Dataclass tracking data quality indicators
    DataSanitizer: Main sanitization engine with comprehensive guards
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    """Data quality and health indicators."""

    total_samples: int = 0
    nan_count: int = 0
    inf_count: int = 0
    zero_variance_count: int = 0
    frozen_sensor_count: int = 0
    dropout_mask: Optional[np.ndarray] = None
    outlier_spacing_count: int = 0
    valid_samples: int = 0
    health_score: float = 1.0  # [0, 1], 1.0 = pristine

    def summary(self) -> str:
        """Return a human-readable health summary."""
        return (
            f"HealthMetrics(total={self.total_samples}, valid={self.valid_samples}, "
            f"NaNs={self.nan_count}, Infs={self.inf_count}, "
            f"zero_var={self.zero_variance_count}, frozen={self.frozen_sensor_count}, "
            f"score={self.health_score:.3f})"
        )


class DataSanitizer:
    """
    Zero-crash data ingestion and fault-tolerance layer.

    Handles:
    - NaN and Inf detection/filtering
    - Zero-variance signal detection
    - Frozen sensor (constant value) detection
    - Hardware dropout masking via plateau detection
    - Outlier filtering for unfolded spacings
    - Automatic logging of all diagnostic actions
    """

    def __init__(
        self,
        nan_threshold: float = 0.1,
        inf_threshold: float = 0.1,
        zero_var_threshold: float = 1e-8,
        frozen_plateau_fraction: float = 0.5,
        spacing_min: float = 1e-5,
        spacing_max: float = 5.0,
    ) -> None:
        """
        Initialize the sanitizer with fault-tolerance thresholds.

        Parameters
        ----------
        nan_threshold : float
            Reject column if > nan_threshold fraction of values are NaN.
        inf_threshold : float
            Reject column if > inf_threshold fraction of values are Inf.
        zero_var_threshold : float
            Flag columns with variance < this threshold as degenerate.
        frozen_plateau_fraction : float
            Flag regions where value stays constant for > this fraction of window as frozen.
        spacing_min, spacing_max : float
            Valid range for unfolded nearest-neighbor spacings; outside this, mark as artifact.
        """
        self.nan_threshold = nan_threshold
        self.inf_threshold = inf_threshold
        self.zero_var_threshold = zero_var_threshold
        self.frozen_plateau_fraction = frozen_plateau_fraction
        self.spacing_min = spacing_min
        self.spacing_max = spacing_max

    def sanitize_dataframe(
        self, df: pd.DataFrame, columns: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, HealthMetrics]:
        """
        Sanitize a pandas DataFrame and return the cleaned version + health report.
        """
        if df.empty:
            logger.warning("Input DataFrame is empty.")
            return df.copy(), HealthMetrics()

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        n_cols = len(columns) if columns else 1
        total_cells = len(df) * n_cols

        # Track total cells so percentage math in reports is accurate across multi-column data
        health = HealthMetrics(total_samples=total_cells)
        df_clean = df.copy()

        for col in columns:
            if col not in df_clean.columns:
                logger.warning(f"Column '{col}' not found in DataFrame.")
                continue

            data = df_clean[col].to_numpy(dtype=np.float64)

            # 1. Detect NaNs
            nan_mask = np.isnan(data)
            nan_cnt = int(nan_mask.sum())
            health.nan_count += nan_cnt
            nan_frac = nan_cnt / len(data) if len(data) > 0 else 0.0

            # 2. Detect and mask Infs -> NaN
            inf_mask = np.isinf(data)
            inf_cnt = int(inf_mask.sum())
            health.inf_count += inf_cnt
            inf_frac = inf_cnt / len(data) if len(data) > 0 else 0.0

            if inf_cnt > 0:
                df_clean.loc[inf_mask, col] = np.nan

            # Column threshold checks
            if nan_frac > self.nan_threshold:
                logger.warning(
                    f"Column '{col}': {nan_frac*100:.1f}% NaN "
                    f"(threshold {self.nan_threshold*100:.1f}%). Flagging as invalid."
                )
                df_clean[col] = np.nan
                continue

            if inf_frac > self.inf_threshold:
                logger.warning(
                    f"Column '{col}': {inf_frac*100:.1f}% Inf "
                    f"(threshold {self.inf_threshold*100:.1f}%). Flagging as invalid."
                )
                df_clean[col] = np.nan
                continue

            # Signal quality checks on non-nan/inf slice
            valid_mask = ~(nan_mask | inf_mask)
            data_valid = data[valid_mask]

            if data_valid.size == 0:
                logger.warning(f"Column '{col}': No valid data after NaN/Inf removal.")
                df_clean[col] = np.nan
                health.zero_variance_count += 1
                continue

            # 3. Check for zero variance
            variance = np.var(data_valid)
            if variance < self.zero_var_threshold:
                logger.warning(
                    f"Column '{col}': Variance {variance:.2e} < threshold "
                    f"{self.zero_var_threshold:.2e}. Marked as degenerate."
                )
                health.zero_variance_count += 1

            # 4. Check for frozen sensor (constant plateaus)
            frozen_mask = self._detect_frozen_regions(data_valid)
            frozen_cnt = int(frozen_mask.sum())
            health.frozen_sensor_count += frozen_cnt

            if frozen_cnt > len(data_valid) * self.frozen_plateau_fraction:
                logger.warning(
                    f"Column '{col}': {frozen_cnt} frozen samples "
                    f"({100*frozen_cnt/len(data_valid):.1f}%). "
                    f"Sensor likely stuck or disconnected."
                )

        # 5. Global Health Calculation (Penalize NaNs, Infs, and Frozen samples)
        corrupted_cell_count = health.nan_count + health.inf_count + health.frozen_sensor_count
        health.valid_samples = max(0, total_cells - corrupted_cell_count)
        health.health_score = max(
            0.0, min(1.0, health.valid_samples / max(total_cells, 1))
        )

        logger.info(f"Data sanitization complete: {health.summary()}")
        return df_clean, health

    def sanitize_array(
        self, arr: np.ndarray, window_size: int = 100
    ) -> Tuple[np.ndarray, HealthMetrics]:
        """
        Sanitize a 1-D numpy array with dropout detection and masking.
        """
        arr = np.asarray(arr, dtype=np.float64).ravel()
        health = HealthMetrics(total_samples=len(arr))

        nan_mask = np.isnan(arr)
        inf_mask = np.isinf(arr)
        health.nan_count = int(nan_mask.sum())
        health.inf_count = int(inf_mask.sum())

        arr_clean = arr.copy()
        arr_clean[nan_mask | inf_mask] = np.nan

        valid_data = arr_clean[~(nan_mask | inf_mask)]
        if valid_data.size > 0:
            variance = np.var(valid_data)
            if variance < self.zero_var_threshold:
                health.zero_variance_count = 1
                logger.warning(
                    f"Array variance {variance:.2e} < threshold. Signal is degenerate."
                )

            frozen_mask = self._detect_frozen_regions(valid_data, window_size=window_size)
            health.frozen_sensor_count = int(frozen_mask.sum())
            if health.frozen_sensor_count > len(valid_data) * self.frozen_plateau_fraction:
                logger.warning(
                    f"Array: {health.frozen_sensor_count} frozen samples detected. "
                    f"Hardware may be disconnected."
                )

        health.dropout_mask = nan_mask | inf_mask
        health.valid_samples = int((~health.dropout_mask).sum())
        health.health_score = health.valid_samples / max(len(arr), 1)

        logger.info(f"Array sanitization complete: {health.summary()}")
        return arr_clean, health

    def filter_spacings(self, spacings: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Filter nearest-neighbor spacings to remove unfolding artifacts.
        """
        spacings = np.asarray(spacings, dtype=np.float64).ravel()
        initial_count = len(spacings)

        valid_mask = (spacings >= self.spacing_min) & (spacings <= self.spacing_max)
        spacings_filtered = spacings[valid_mask]
        outlier_count = initial_count - len(spacings_filtered)

        if outlier_count > 0:
            logger.warning(
                f"Filtered {outlier_count} outlier spacings "
                f"(range [{self.spacing_min}, {self.spacing_max}])"
            )

        if len(spacings_filtered) > 0:
            mean_spacing = spacings_filtered.mean()
            if mean_spacing > 1e-12:
                spacings_filtered = spacings_filtered / mean_spacing

        return spacings_filtered, outlier_count

    @staticmethod
    def _detect_frozen_regions(
        data: np.ndarray, window_size: int = 50, tolerance: float = 1e-8
    ) -> np.ndarray:
        """
        Detect regions where data is frozen (constant or near-constant).
        """
        if len(data) < window_size:
            window_size = max(1, len(data) // 2)

        frozen = np.zeros(len(data), dtype=bool)
        for i in range(len(data) - window_size + 1):
            window = data[i : i + window_size]
            if np.std(window) < tolerance:
                frozen[i : i + window_size] = True
        return frozen

    def generate_diagnostic_report(self, metrics: HealthMetrics) -> str:
        """
        Generate a detailed text report of data health.
        """
        valid_pct = 100.0 * metrics.valid_samples / max(metrics.total_samples, 1)
        lines = [
            "=" * 60,
            "DATA HEALTH DIAGNOSTIC REPORT",
            "=" * 60,
            f"Total samples (cells):   {metrics.total_samples}",
            f"Valid samples:           {metrics.valid_samples} ({valid_pct:.1f}%)",
            f"NaN count:               {metrics.nan_count}",
            f"Inf count:               {metrics.inf_count}",
            f"Zero-variance signals:   {metrics.zero_variance_count}",
            f"Frozen sensor regions:   {metrics.frozen_sensor_count}",
            f"Outlier spacings:        {metrics.outlier_spacing_count}",
            f"Overall health score:    {metrics.health_score:.3f} (0=bad, 1=perfect)",
            "=" * 60,
        ]
        return "\n".join(lines)
