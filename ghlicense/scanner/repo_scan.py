"""Repository scanning functionality."""
import sys
import time
import logging
import asyncio
import urllib.request
import urllib.error
from ghlicense import repobase

logger = logging.getLogger(__name__)


def print_license_status(msg):
    """Print license status messages with a progress bar."""
    sys.stdout.write(" " * 52)
    sys.stdout.write("\r")
    sys.stdout.flush()
    logger.info(msg)


def update_progress_bar(current, total):
    """Display a progressbar using ASCII characters alongwith the status."""
    sys.stdout.write("|")
    sys.stdout.write("#" * int(current * 40 / total))
    sys.stdout.write("-" * (40 - int(current * 40 / total)))
    sys.stdout.write(" | Done " + str(int(current * 100 / total)) + "% \r")
    sys.stdout.flush()


def _fetch_license_file(url):
    """Synchronous function to fetch a license file (runs in executor)."""
    urllib.request.urlretrieve(url)


async def loop_repo_scan(repo, license_files, repo_provider=None):
    """Scan a single repository for license files (async version).
    
    Args:
        repo: Repository object with raw_base_url, repo_url, full_name, and fork attributes
        license_files: List of license file names to check
        
    Returns:
        Tuple of (output_string, count_license, count_no_license, count_forked)
    """
    license_url = repo.raw_base_url
    repo_url = repo.repo_url
    to_print = ""
    count_license = 0
    count_no_license = 0
    count_forked = 0

    # Look for a License file in the root directory of the repo
    for license_file in license_files:
        missing = True
        try:
            # Run synchronous urllib request in executor to avoid blocking
            await asyncio.to_thread(_fetch_license_file, license_url + license_file)
        except urllib.error.HTTPError as err:
            if err.code == 404:
                missing = True
        except Exception:
            # Other errors (connection issues, timeouts) also mean missing
            missing = True
        else:
            license_status = f"✓ Found: {license_url}{license_file}"
            print_license_status(license_status)
            to_print += f"Repo: {repo.full_name}\nURL: {repo_url} \n"
            to_print += f"{license_status} \n"
            missing = False
            count_license += 1
            break

    if missing:
        license_status = "✗ Missing the license, this repo is proprietary!"
        print_license_status(license_status)
        to_print += f"Repo: {repo.full_name}\nURL: {repo_url} \n"
        to_print += f"{license_status} \n"
        count_no_license += 1
        if repo.fork:
            to_print += " ! Is a fork, check the original or create a PR!\n"
            count_forked += 1

    to_print += "\n"
    return to_print, count_license, count_no_license, count_forked


async def args_scan(ARGS):
    """The scan command (async version) - scan all public repos of a user for license files.
    
    Args:
        ARGS: Command line arguments with attributes:
            - scan: username to scan
            - provider: repository provider (github, bitbucket, gitlab)
            - report: optional report filename
    """
    # Initialise specified repo provider
    # (or use the default provider, if one is not specified)
    repo_provider = repobase.get_provider(ARGS.provider)

    # Obtain the username passed on the cmd-line in "scan" mode
    user = repo_provider(ARGS.scan)

    # Create the specified license report file
    # (or use the default license report file name, if one is not specified)
    report_file_name = "default"
    if ARGS.report is None:
        report_file_name = f"{ARGS.scan}-{ARGS.provider}-license-report"
        logger.info(f' No report file name found, using default "{report_file_name}"')
    else:
        report_file_name = ARGS.report

    # Start scanning user's public repos
    with open(report_file_name, "w", encoding="UTF-8") as report_file:
        report_file.write("Last scan done on: " + time.strftime("%c") + "\n")
        report_file.write("Scan report of user: " + ARGS.scan + "\n")
        
        # Track license status for filtering
        licensed_repos = []
        unlicensed_repos = []
        
        repos = list(user.get_repos())
        count_total = len(repos)
        count_current = 0
        count_license = 0
        count_no_license = 0
        count_forked = 0

        license_base_name = "license"
        # This is ordered by the most common extensions
        license_extensions = ["", ".md", ".txt"]
        license_files = []

        # This is ordered like this because most license file names are in full caps
        for license_name in [license_base_name.upper(), license_base_name]:
            license_files.extend([license_name + extension for extension in license_extensions])

        to_print = ''
        # For each repo found
        logger.info('Downloading Repository list')

        # Process repos concurrently using asyncio.gather
        # Using a semaphore to limit concurrent requests (avoid rate limiting)
        semaphore = asyncio.Semaphore(4)  # Match previous ThreadPool(processes=4)

        async def scan_with_progress(repo):
            """Scan a single repo with semaphore control and progress updates."""
            nonlocal count_current, count_license, count_no_license, count_forked, licensed_repos, unlicensed_repos
            async with semaphore:
                logger.info(repo.full_name)
                count_current += 1
                result = await loop_repo_scan(repo, license_files)
                _to_print, _count_license, _count_no_license, _count_forked = result
                update_progress_bar(count_current, count_total)
                # Track repos by license status for filtering
                if _count_license > 0:
                    licensed_repos.append(_to_print)
                elif _count_no_license > 0:
                    unlicensed_repos.append(_to_print)
                return result

        # Create tasks for all repos
        tasks = [scan_with_progress(repo) for repo in repos]
        results = await asyncio.gather(*tasks)

        # Aggregate results
        for _to_print, _count_license, _count_no_license, _count_forked in results:
            to_print += _to_print
            count_license += _count_license
            count_no_license += _count_no_license
            count_forked += _count_forked

        # Filter repos based on --show option
        show_filter = ARGS.show if hasattr(ARGS, 'show') and ARGS.show else "all"
        report_file.write(f"License status filter: {show_filter}\n\n")
        
        # Filter and aggregate output
        filtered_output = ""
        if show_filter == "all":
            filtered_output = to_print
        elif show_filter == "licensed":
            for repo_content in licensed_repos:
                filtered_output += repo_content
        elif show_filter == "unlicensed":
            for repo_content in unlicensed_repos:
                filtered_output += repo_content
        
        report_file.write(filtered_output)
        report_file.write("\nStatistics: \n")
        report_file.write(f"Repos with License: {count_license}\n")
        report_file.write(f"Repos without License: {count_no_license}\n")
        report_file.write(f"Repos without License and forked: {count_forked}\n")
        report_file.write(f"Total Repos: {count_no_license + count_license}\n")
        report_file.close()
