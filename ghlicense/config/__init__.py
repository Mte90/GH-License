"""Configuration storage module."""
from ghlicense.config.storage import (
    save_last_used_licenses,
    load_last_used_licenses,
    pick_license_from_last_used,
)

__all__ = [
    "save_last_used_licenses",
    "load_last_used_licenses",
    "pick_license_from_last_used",
]