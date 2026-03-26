"""Configuration storage functionality."""
import os
import sys
import logging
from configparser import ConfigParser

logger = logging.getLogger(__name__)


def save_last_used_licenses(last_used_licenses):
    """Saves the most recently uses licenses in the config file. If no config
    file exists, it will create one.
    
    Args:
        last_used_licenses: a sequence of the three most recently used licenses
        in order of most recently used first.
    """
    config = ConfigParser()
    config_file_path = os.path.expanduser("~/.gh-license/config.ini")
    config.read(config_file_path)

    # make the dirs if necessary.
    if not os.path.exists(os.path.dirname(config_file_path)):
        os.makedirs(os.path.dirname(config_file_path))

    if "lastUsed" not in config:
        config["lastUsed"] = {}
    config["lastUsed"]["lastUsedLicenses"] = ",".join(last_used_licenses)
    with open(config_file_path, "w", encoding="UTF-8") as config_file:
        config.write(config_file)


def load_last_used_licenses():
    """Returns an array of the last used licenses, in order of
    most recently used first. Returns an empty array if no license has been
    previously used.
    
    Returns:
        List of license names (most recent first), or empty list
    """
    config = ConfigParser()
    if not config.read(os.path.expanduser("~/.gh-license/config.ini")):
        return []
    try:
        return config["lastUsed"]["lastUsedLicenses"].split(",")
    except KeyError:
        return []


def pick_license_from_last_used(last_used_licenses, licenses_path):
    """Assumes the user did not select a license. Presents them with
    their most recently used licenses from last_used_licenses and allows
    them to select one (or any other license).

    Returns the string name of the selected license.
    
    Args:
        last_used_licenses: a sequence of the three most recently used licenses
        in order of most recently used first.
    licenses_path: Path to the licenses.json file (for listing all licenses)
    
    Returns:
        The selected license name (string)
    """
    from ghlicense.license.manager import print_license_list
    
    logger.info("You have not selected a license, ", end="")
    if last_used_licenses:
        logger.info("the last licenses you've used are: ")
        for i, license_name in enumerate(last_used_licenses):
            logger.info(f"[{i+1}]{license_name}", end="")
            if i < len(last_used_licenses) - 1:
                logger.info(", ", end="")
        logger.info("\nPress [1], [2], and so on to download the license,\nor e", end="")
    else:
        logger.info("you also have no previously used licenses.\n", end="")

    logger.info("Enter the name of the license you want, or press " + "[n] to see a description of every license.")
    license_input = input("")

    # Print the list and then exit
    if license_input.lower() == "n":
        print_license_list(licenses_path)
        sys.exit(1)

    # Return the name of the selected license if possible, or just return the input license
    try:
        selected_license = last_used_licenses[int(license_input) - 1]
        return selected_license
    except (ValueError, IndexError):
        return license_input
