"""Pytest configuration for gh-license test suite."""

# Pre-block pytestqt BEFORE pytest loads
import pluggy
pm = pluggy.PluginManager('pytest')
pm.set_blocked('pytestqt')
