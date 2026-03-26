"""License management functionality."""
import os
import sys
import logging
import json
import urllib.request
import subprocess

logger = logging.getLogger(__name__)


def update_license(url, name, badge):
    """Update the project with the specified License text and badge.
    
    Args:
        url: URL to download the license from
        name: Name of the license
        badge: Badge to add to README
        
    Returns:
        Name of the README file that was updated, or empty string if none
    """
    logger.info(f"License {name} download in progress.")
    # If a file "LICENSE" does NOT exist in the repo
    if not os.path.isfile("LICENSE"):
        # Obtain the License text and save it as the file LICENSE
        urllib.request.urlretrieve(url, "LICENSE")
        logger.info(f"License {name} saved as file LICENSE.")

    # If a README file by any of these names exists
    # then add License details and badge to it.
    readme_names = [
        "README.md",
        "Readme.md",
        "README.txt",
        "readme",
        "README",
        "readme.txt",
        "readme.md",
        "read_me",
        "Read_me",
        "READ_ME",
    ]
    for readme_name in readme_names:
        if os.path.isfile(readme_name):
            # Open the file for reading/writing
            readme_file = open(readme_name, "r+", encoding="UTF-8")

            # Load entire file as a list of lines
            text = [i for i in readme_file.readlines()]

            # Insert the License name and badge at the beginning of the file
            readme_file.seek(0)
            if text and text[0][0] == "#":
                readme_file.write(text[0])
                text.pop(0)
            readme_file.write(f"[![License]{badge}   \n")
            readme_file.write("".join(text))
            readme_file.close()
            logger.info(f"Added badge license for {name} in {readme_name}.")
            return readme_name

    return ""


def print_license_list(licenses_path):
    """Print the license list from the JSON file provided with the package.
    
    Args:
        licenses_path: Path to the licenses.json file
    """
    try:
        with open(licenses_path, "r", encoding="UTF-8") as file:
            licenses_data = json.load(file)
        for _license in licenses_data:
            name = _license["name"]
            description = _license["description"]
            logger.info(name)
            logger.info(f"    {description}")
    except FileNotFoundError:
        logger.error("licenses.json file not found.")


def update_license_from_json(chosen_license, licenses_path):
    """Check if the license provided exists in the package otherwise proceed.
    
    Args:
        chosen_license: Name of the license to update
        licenses_path: Path to the licenses.json file
        
    Exits:
        sys.exit(1) if license not found
    """
    logger.info("Updating license from JSON...")
    # Read licenses from JSON file
    with open(licenses_path, "r", encoding="UTF-8") as file:
        licenses = json.load(file)
    # Check if chosen_license exists in licenses
    license_info = None
    for _license in licenses:
        if _license["name"] == chosen_license:
            license_info = _license
            break

    if license_info:
        logger.info(f"License found: {license_info['name']}")
        logger.info("License update successful.")
        return update_license(license_info["link"], chosen_license, license_info["badge"])

    if isinstance(chosen_license, bool):
        logger.error("No license provided")
    else:
        logger.error(f"License {chosen_license} not found!")
    sys.exit(1)


def git_commit(ARGS, name, readme_name):
    """Commit license changes to git repository.
    
    Args:
        ARGS: Command line arguments with optional 'origin' attribute
        name: License name for commit message
        readme_name: Name of the README file that was modified
        
    Returns:
        None (prints status messages)
    """

    def is_git_repo():
        """Check if current directory is a git repository."""
        result = subprocess.run(["git", "rev-parse", "--git-dir"],
                              capture_output=True,
                              text=True)
        return result.returncode == 0

    if not is_git_repo():
        logger.info("Not a git repository. Skipping git operations.")
        return

    if not os.path.exists("LICENSE"):
        logger.info("LICENSE file not found. Skipping git operations.")
        return

    # All git commands wrapped in is_git_repo() check
    try:
        subprocess.run(["git", "add", "LICENSE"], check=True)
        subprocess.run(["git", "add", readme_name], check=True)
        subprocess.run(["git", "commit", "-m", f"Added {name} LICENSE"], check=True)

        # Get current branch safely
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                              capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        logger.info(f"Current Git branch is: {current_branch}")

        # Push changes
        if ARGS.origin is not None:
            subprocess.run(["git", "push", ARGS.origin, current_branch], check=True)
        else:
            subprocess.run(["git", "push", "origin", current_branch], check=True)

    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        logger.error(f"Error output: {e.stderr.strip() if e.stderr else ''}")


def args_license(ARGS, licenses_path):
    """The license command - download and apply a license."""
    from ghlicense.config.storage import (
        load_last_used_licenses,
        pick_license_from_last_used,
        save_last_used_licenses,
    )
    last_used_licenses = load_last_used_licenses()
    chosen_license = ARGS.license
    if not ARGS.license:
        chosen_license = pick_license_from_last_used(last_used_licenses, licenses_path)
    readme_name = update_license_from_json(chosen_license, licenses_path)
    git_commit(ARGS, chosen_license, readme_name)
    last_used_licenses.insert(0, chosen_license)
    unique_last_used = []
    for item in last_used_licenses:
        if len(unique_last_used) >= 3:
            break
        if item in unique_last_used:
            continue
        unique_last_used.append(item)
    save_last_used_licenses(unique_last_used[:3])
    sys.exit(1)
