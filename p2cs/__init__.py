"""
P2CS — Publication-to-Code Synthesis Platform

risk: low
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("p2cs")
except PackageNotFoundError:
    __version__ = "0.1.0-alpha"

__all__ = ["__version__"]
