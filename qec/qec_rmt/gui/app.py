"""
QEC-RMT-Studio: Interactive PyQt6 Desktop Application.

A production-grade GUI for real-time RMT spectral analysis and QEC
logical error rate visualization with interactive parameter controls.

Main entry point: main()
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Optional
from pyqtgraph.Qt import QtCore
import numpy as np
import pandas as pd
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QFileDialog,
    QSpinBox,
    QDoubleSpinBox,
    QGroupBox,
    QMessageBox,
    QProgressBar,
    QTextEdit,
)
from PyQt6.QtGui import QFont, QIcon
import pyqtgraph as pg

from qec_rmt.core import DataSanitizer, RMTEngine, QECEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


class ProcessingWorker(QThread):
    """Background worker thread for computationally intensive tasks."""

    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, task_func, *args, **kwargs):
        """Initialize with a task function and arguments."""
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Execute the task in a background thread."""
        try:
            result = self.task_func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as exc:
            logger.error(f"Worker thread error: {exc}")
            self.error.emit(str(exc))


class Tab1_TelemetryAndIngestion(QWidget):
    """Tab 1: Raw sensor data ingestion and quality monitoring."""

    def __init__(self):
        super().__init__()
        self.data = None
        self.health_metrics = None
        self.init_ui()

    def init_ui(self):
        """Initialize the telemetry tab UI."""
        layout = QVBoxLayout()

        # File loading
        file_group = QGroupBox("Data Source")
        file_layout = QHBoxLayout()
        self.load_csv_btn = QPushButton("Load CSV")
        self.load_csv_btn.clicked.connect(self.load_csv)
        file_layout.addWidget(self.load_csv_btn)
        file_layout.addStretch()
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Data quality display
        quality_group = QGroupBox("Data Health Report")
        quality_layout = QVBoxLayout()
        self.health_text = QTextEdit()
        self.health_text.setReadOnly(True)
        self.health_text.setFont(QFont("Courier", 9))
        quality_layout.addWidget(self.health_text)
        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)

        # Raw signal plot
        plot_group = QGroupBox("Raw Signal Preview")
        plot_layout = QVBoxLayout()
        self.raw_plot = pg.PlotWidget(title="Sensor Channels (First 1000 samples)")
        self.raw_plot.setLabel("bottom", "Sample Index")
        self.raw_plot.setLabel("left", "Standardized Value")
        plot_layout.addWidget(self.raw_plot)
        plot_group.setLayout(plot_layout)
        layout.addWidget(plot_group)

        layout.addStretch()
        self.setLayout(layout)

    def load_csv(self):
        """Load and display a CSV file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Sensor Data", "", "CSV Files (*.csv);;All Files (*)"
        )
        if not filepath:
            return

        try:
            df = pd.read_csv(filepath)
            sanitizer = DataSanitizer()
            df_clean, self.health_metrics = sanitizer.sanitize_dataframe(df)
            self.data = df_clean

            # Display health report
            report = sanitizer.generate_diagnostic_report(self.health_metrics)
            self.health_text.setText(report)

            # Plot first 1000 samples
            self.plot_raw_data()
            logger.info(f"Loaded CSV: {filepath}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to load CSV: {exc}")

    def plot_raw_data(self):
        """Plot raw sensor data."""
        if self.data is None:
            return

        self.raw_plot.clear()
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        colors = ["red", "green", "blue", "orange", "purple", "cyan"]

        for idx, col in enumerate(numeric_cols[:6]):
            data = self.data[col].values[:1000]
            color = colors[idx % len(colors)]
            self.raw_plot.plot(
                data, name=col, pen=pg.mkPen(color, width=1.5), alpha=0.7
            )

        self.raw_plot.legend(offset=(50, 30))


class Tab2_RMTSpectralAnalysis(QWidget):
    """Tab 2: RMT spectral analysis and Brody fitting visualization."""

    def __init__(self):
        super().__init__()
        self.rmt_results = None
        self.sanitizer = DataSanitizer()
        self.rmt_engine = RMTEngine()
        self.init_ui()

    def init_ui(self):
        """Initialize the RMT analysis tab UI."""
        layout = QVBoxLayout()

        # Control panel
        control_group = QGroupBox("RMT Pipeline Parameters")
        control_layout = QHBoxLayout()

        control_layout.addWidget(QLabel("Window Length:"))
        self.win_len_spin = QSpinBox()
        self.win_len_spin.setRange(50, 1000)
        self.win_len_spin.setValue(200)
        control_layout.addWidget(self.win_len_spin)

        control_layout.addWidget(QLabel("Legendre Degree:"))
        self.leg_deg_spin = QSpinBox()
        self.leg_deg_spin.setRange(2, 10)
        self.leg_deg_spin.setValue(4)
        control_layout.addWidget(self.leg_deg_spin)

        self.analyze_btn = QPushButton("Run RMT Analysis")
        self.analyze_btn.clicked.connect(self.run_rmt_analysis)
        control_layout.addWidget(self.analyze_btn)

        control_layout.addStretch()
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Eigenvalue histogram
        eigen_group = QGroupBox("Eigenvalue Spectrum")
        eigen_layout = QVBoxLayout()
        self.eigen_plot = pg.PlotWidget(title="Wishart Eigenvalues (All Windows)")
        self.eigen_plot.setLabel("bottom", "Eigenvalue")
        self.eigen_plot.setLabel("left", "Frequency")
        eigen_layout.addWidget(self.eigen_plot)
        eigen_group.setLayout(eigen_layout)
        layout.addWidget(eigen_group)

        # Spacing distribution with Brody fit
        spacing_group = QGroupBox("Nearest-Neighbor Spacing Distribution")
        spacing_layout = QVBoxLayout()
        self.spacing_plot = pg.PlotWidget(
            title="P(s) Histogram vs Brody Fit"
        )
        self.spacing_plot.setLabel("bottom", "Normalized Spacing s")
        self.spacing_plot.setLabel("left", "Probability Density P(s)")
        self.spacing_plot.setLogMode(x=False, y=False)
        spacing_layout.addWidget(self.spacing_plot)
        spacing_group.setLayout(spacing_layout)
        layout.addWidget(spacing_group)

        # Statistics display
        stats_group = QGroupBox("RMT Statistics")
        stats_layout = QVBoxLayout()
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("Courier", 9))
        stats_layout.addWidget(self.stats_text)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        self.setLayout(layout)

    def run_rmt_analysis(self):
        """Run the full RMT pipeline on loaded data."""
        logger.info("Starting RMT analysis...")
        # Placeholder: in a full app, this would load data from Tab1
        QMessageBox.information(self, "Info", "RMT analysis demo (data from Tab1)")


class Tab3_QECThresholdAndErrorMapping(QWidget):
    """Tab 3: Interactive QEC threshold visualization and error-rate mapping."""

    def __init__(self):
        super().__init__()
        self.qec_engine = QECEngine()
        self.w_array = np.linspace(0, 1, 100)
        self.init_ui()

    def init_ui(self):
        """Initialize the QEC threshold tab UI."""
        layout = QVBoxLayout()

        # Parameter controls
        control_group = QGroupBox("Surface Code Parameters")
        control_layout = QHBoxLayout()

        control_layout.addWidget(QLabel("Code Distance d:"))
        self.d_spin = QSpinBox()
        self.d_spin.setRange(2, 7)
        self.d_spin.setValue(3)
        self.d_spin.valueChanged.connect(self.update_qec_plot)
        control_layout.addWidget(self.d_spin)

        control_layout.addWidget(QLabel("Threshold p_th:"))
        self.p_th_spin = QDoubleSpinBox()
        self.p_th_spin.setRange(0.001, 0.1)
        self.p_th_spin.setValue(0.011)
        self.p_th_spin.setDecimals(4)
        self.p_th_spin.setSingleStep(0.001)
        self.p_th_spin.valueChanged.connect(self.update_qec_plot)
        control_layout.addWidget(self.p_th_spin)

        control_layout.addWidget(QLabel("Prefactor C:"))
        self.c_spin = QDoubleSpinBox()
        self.c_spin.setRange(0.01, 1.0)
        self.c_spin.setValue(0.1)
        self.c_spin.setDecimals(3)
        self.c_spin.setSingleStep(0.01)
        self.c_spin.valueChanged.connect(self.update_qec_plot)
        control_layout.addWidget(self.c_spin)

        control_layout.addStretch()
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Error-rate plot
        plot_group = QGroupBox("Logical Error Rate E_L vs Chaoticity w")
        plot_layout = QVBoxLayout()
        self.e_l_plot = pg.PlotWidget(title="E_L(w) Scaling Relation")
        self.e_l_plot.setLabel("bottom", "Brody Parameter w")
        self.e_l_plot.setLabel("left", "Logical Error Rate E_L")
        self.e_l_plot.setLogMode(x=False, y=True)
        plot_layout.addWidget(self.e_l_plot)
        plot_group.setLayout(plot_layout)
        layout.addWidget(plot_group)

        # Noise mapping plot (w -> p_phys)
        noise_group = QGroupBox("Physical Fault Probability")
        noise_layout = QVBoxLayout()
        self.p_phys_plot = pg.PlotWidget(title="p_phys(w) Mapping")
        self.p_phys_plot.setLabel("bottom", "Brody Parameter w")
        self.p_phys_plot.setLabel("left", "p_phys")
        noise_layout.addWidget(self.p_phys_plot)
        noise_group.setLayout(noise_layout)
        layout.addWidget(noise_group)

        # Initial plot
        self.update_qec_plot()
        self.setLayout(layout)

    def update_qec_plot(self):
        """Update QEC plots with current parameter values."""
        d = self.d_spin.value()
        p_th = self.p_th_spin.value()
        c = self.c_spin.value()

        # Update engine parameters
        self.qec_engine.d = d
        self.qec_engine.p_th = p_th
        self.qec_engine.C = c

        # Compute E_L for range of w
        e_l_vals = []
        p_phys_vals = []
        for w in self.w_array:
            p_phys = self.qec_engine.w_to_p_phys(w)
            e_l = self.qec_engine.logical_error_rate_analytical(p_phys)
            e_l_vals.append(e_l)
            p_phys_vals.append(p_phys)

        e_l_vals = np.array(e_l_vals)
        p_phys_vals = np.array(p_phys_vals)

        # Plot E_L vs w
        self.e_l_plot.clear()
        self.e_l_plot.plot(
            self.w_array,
            e_l_vals,
            pen=pg.mkPen("blue", width=2),
            symbol="o",
            symbolSize=4,
            name="E_L(w)",
        )
        # Add threshold line

        # Use the explicit Qt PenStyle enum instead of the integer 2
        self.e_l_plot.addLine(
              y=p_th, 
              pen=pg.mkPen("red", style=QtCore.Qt.PenStyle.DashLine), 
              label="Threshold"
          )

        # Plot p_phys vs w
        self.p_phys_plot.clear()
        self.p_phys_plot.plot(
            self.w_array,
            p_phys_vals,
            pen=pg.mkPen("green", width=2),
            symbol="s",
            symbolSize=4,
            name="p_phys(w)",
        )


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("QEC-RMT-Studio: Quantum Error Correction & RMT Analysis")
        self.setGeometry(100, 100, 1400, 900)

        # Create tabs
        self.tabs = QTabWidget()
        self.tab1 = Tab1_TelemetryAndIngestion()
        self.tab2 = Tab2_RMTSpectralAnalysis()
        self.tab3 = Tab3_QECThresholdAndErrorMapping()

        self.tabs.addTab(self.tab1, "1. Telemetry & Ingestion")
        self.tabs.addTab(self.tab2, "2. RMT Spectral Analysis")
        self.tabs.addTab(self.tab3, "3. QEC Threshold & Error Mapping")

        self.setCentralWidget(self.tabs)
        logger.info("QEC-RMT-Studio application initialized.")


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
