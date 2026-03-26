"""Legacy functions module - re-exports from appropriate modules."""
import logging

logger = logging.getLogger(__name__)


def print_license_list(licenses_path):
    """Print the license list from the JSON file provided with the package"""
    from ghlicense.license.manager import print_license_list as _print_license_list
    _print_license_list(licenses_path)


def args_license(ARGS, licenses_path):
    """The license command"""
    from ghlicense.license.manager import args_license as _args_license
    _args_license(ARGS, licenses_path)


# Re-export from scanner for backward compatibility
from ghlicense.scanner import print_license_status, update_progress_bar, loop_repo_scan, args_scan

# Re-export from license for backward compatibility
from ghlicense.license.manager import update_license, update_license_from_json, git_commit

# Re-export from config for backward compatibility
from ghlicense.config.storage import save_last_used_licenses, load_last_used_licenses, pick_license_from_last_used
__all__ = [
    "print_license_status",
    "update_progress_bar",
    "loop_repo_scan",
    "args_scan",
    "print_license_list",
    "args_license",
    "update_license",
    "update_license_from_json",
    "git_commit",
    "save_last_used_licenses",
    "load_last_used_licenses",
    "pick_license_from_last_used",
]