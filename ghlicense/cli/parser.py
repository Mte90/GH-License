"""CLI argument parser configuration."""

import sys
from argparse import REMAINDER, ArgumentParser, RawTextHelpFormatter
from ghlicense import repobase

ENHANCED_DESCRIPTION = """
    This script scans every repo of the specified user for a license
    file. If a license can't be found, the script will upload a
    a specified license to your repo.

    Choose a license on http://choosealicense.com/licenses/ or use
    http://www.addalicense.com/.

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

DISABLED_PROVIDERS_STR = ", ".join(DISABLED_PROVIDERS) if DISABLED_PROVIDERS else ""
ENABLED_PROVIDERS_STR = ", ".join(ENABLED_PROVIDERS)
ERR_PROVIDERS_TXT = f"(errored providers: {DISABLED_PROVIDERS_STR})"

PARSER.add_argument("--scan", help="Scan repo of the user, arguments: [User_nick]", action="store")
PARSER.add_argument("--license", help="Download a license file, arguments: [License_name]", nargs="?", const=True)
PARSER.add_argument("--licenselist", "--license-list", help="Show licenses available", action="store_true")
PARSER.add_argument(
    "--provider",
    help=f"Repository provider. Defaults to github. Available providers: {ENABLED_PROVIDERS} {ERR_PROVIDERS_TXT}",
    action="store",
    default="github",
)
PARSER.add_argument("--show", help="Filter by license status (all/licensed/unlicensed)", action="store", default="all", choices=["all", "licensed", "unlicensed"])
PARSER.add_argument("--report", help="The report filename for scan (optional)", action="store")
PARSER.add_argument("--origin", help="The origin of the git repo (optional)", action="store")
PARSER.add_argument("args", nargs=REMAINDER)


def parse_args():
    """Parse command line arguments, handling pytest collection."""
    # Check if running under pytest (pytest collection doesn't have subcommand)
    if len(sys.argv) < 2:
        # When running pytest, don't exit - return default args
        # This allows test collection to work
        class DefaultArgs:
            scan = None
            license = None
            licenselist = False
            provider = "github"
            report = None
            origin = None
            show = "all"
            args = []

        return DefaultArgs()
    return PARSER.parse_args()