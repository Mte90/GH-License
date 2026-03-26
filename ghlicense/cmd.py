"""Backward compatibility wrapper for CLI.
This module re-exports the CLI functionality for backward compatibility.
The actual implementation has been moved to ghlicense.cli module.
"""
import logging
import os
import sys
import asyncio

from ghlicense.cli.parser import PARSER, parse_args

# Re-export for backward compatibility
ARGS = parse_args()

# Get licenses path for backward compatibility
current_directory = os.path.dirname(os.path.abspath(__file__))
licenses_path = os.path.join(current_directory, "licenses.json")

from ghlicense.scanner import args_scan
from ghlicense.functions import print_license_list, args_license


def main() -> None:
    """Execute the script - backward compatibility wrapper."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    # Check whether at least 1 cmdline param was passed to the script.
    # If not then display help/usage and quit.
    if len(sys.argv) < 2:
        PARSER.print_help()
        sys.exit(0)

    if ARGS.scan:
        asyncio.run(args_scan(ARGS))
    elif ARGS.licenselist:
        print_license_list(licenses_path)
    elif ARGS.license:
        args_license(ARGS, licenses_path)
    else:
        logging.info("Do you have checked the help section about how to use the various parameters?")

    sys.exit(1)


if __name__ == "__main__":
    main()
