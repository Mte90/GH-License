"""CLI command handlers.

This module re-exports command handlers from functions.py for use in the CLI module.
"""

from ghlicense.scanner import args_scan
from ghlicense.functions import args_license, print_license_list

__all__ = ["args_scan", "args_license", "print_license_list"]