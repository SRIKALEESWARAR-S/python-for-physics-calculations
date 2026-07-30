"""
Core computational engines for RMT analysis and QEC noise mapping.

Modules:
    sanitizer: Data cleaning, health guards, and fault tolerance
    rmt_engine: Hankel embedding, Legendre unfolding, Brody MLE
    qec_engine: Pauli channels and surface code logical error rates
"""

from .sanitizer import DataSanitizer
from .rmt_engine import RMTEngine
from .qec_engine import QECEngine

__all__ = ["DataSanitizer", "RMTEngine", "QECEngine"]
