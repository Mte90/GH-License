"""CLI module for gh-license.

This module provides the command-line interface for gh-license.
"""
import os
import sys
import logging
import asyncio

from ghlicense.cli.parser import PARSER, parse_args
from ghlicense.cli.commands import args_scan, args_license, print_license_list

logger = logging.getLogger(__name__)

# Get the licenses path
current_directory = os.path.dirname(os.path.abspath(__file__))
licenses_path = os.path.join(current_directory, "licenses.json")


def main():
    """Execute the script."""
    args = parse_args()

    # Check whether at least 1 cmdline param was passed to the script.
    # If not then display help/usage and quit.
    if len(sys.argv) < 2:
        PARSER.print_help()
        sys.exit(0)

    if args.scan:
        asyncio.run(args_scan(args))
    elif args.licenselist:
        print_license_list(licenses_path)
    elif args.license:
        args_license(args, licenses_path)
    else:
        logger.info("Do you have checked the help section about how to use the various parameters?")

    sys.exit(1)


__all__ = ["main", "parse_args", "PARSER"]
