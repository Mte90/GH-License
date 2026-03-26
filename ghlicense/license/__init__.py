"""License management module."""
from ghlicense.license.manager import (
    update_license,
    print_license_list,
    update_license_from_json,
    git_commit,
    args_license,
)

__all__ = [
    "update_license",
    "print_license_list",
    "update_license_from_json",
    "git_commit",
    "args_license",
]