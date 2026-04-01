"""Pytest configuration for gh-license test suite."""
import sys

# Pre-block pytestqt and PySide6 BEFORE pytest loads
# This prevents the broken pytestqt from loading
sys.modules['pytestqt'] = type(sys)('pytestqt')

# Fix PySide6 version issue
import PySide6
if not hasattr(PySide6, '__version__'):
    PySide6.__version__ = '6.0.0'
