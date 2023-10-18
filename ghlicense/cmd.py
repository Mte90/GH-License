#!/usr/bin/env python3

import os
import sys
from argparse import REMAINDER, ArgumentParser, RawTextHelpFormatter

from ghlicense import repobase
from ghlicense.functions import (
    print_license_list,
    args_scan,
    args_license,
)
from ghlicense.providers import github, bitbucket, gitlab

ENHANCED_DESCRIPTION = """
    This script scans every repo of the specified user for a license
    file. If a license can't be found, the script will upload a
    a specified license to your repo.\n
    Choose a license on http://choosealicense.com/licenses/ or use
    http://www.addalicense.com/.\n
    Remember, without a license file, your project is proprietary!
"""

# Load all the providers
ENABLED_PROVIDERS, DISABLED_PROVIDERS = repobase.get_providers()

# Parse the cmdline and initialise args
PARSER = ArgumentParser(
    description="GitHosting License checker and downloader",
    epilog=ENHANCED_DESCRIPTION,
    formatter_class=RawTextHelpFormatter,
)

disabled_providers = ", ".join(DISABLED_PROVIDERS) if DISABLED_PROVIDERS else ""
enabled_providers = ", ".join(ENABLED_PROVIDERS)
ERR_PROVIDERS_TXT = f"(errored providers: {disabled_providers})"

PARSER.add_argument("--scan", help="Scan repo of the user, arguments: [User_nick]", action="store")
PARSER.add_argument("--license", help="Download a license file, arguments: [License_name]", nargs="?", const=True)
PARSER.add_argument("--licenselist", "--license-list", help="Show licenses available", action="store_true")
PARSER.add_argument(
    "--provider",
    help=f"Repository provider. Defaults to github. Available providers: {enabled_providers} {ERR_PROVIDERS_TXT}",
    action="store",
    default="github",
)
PARSER.add_argument("--report", help="The report filename for scan (optional)", action="store")
PARSER.add_argument("--origin", help="The origin of the git repo (optional)", action="store")
PARSER.add_argument("args", nargs=REMAINDER)

ARGS = PARSER.parse_args()

# Check whether at least 1 cmdline param was passed to the script.
# If not then display help/usage and quit.
if len(sys.argv) < 2:
    PARSER.print_help()
    sys.exit(0)

current_directory = os.path.dirname(os.path.abspath(__file__))
licenses_path = os.path.join(current_directory, "licenses.json")


def main():
    """Execute the script."""

    if ARGS.scan:
        args_scan(ARGS)
    elif ARGS.licenselist:
        print_license_list(licenses_path)
    elif ARGS.license:
        args_license(ARGS, licenses_path)
    else:
        print("Do you have checked the help section about how to use the various parameters?")

    sys.exit(1)


if __name__ == "__main__":
    main()
