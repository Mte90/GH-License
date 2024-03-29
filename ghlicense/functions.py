"""Functions used by the tool"""
import sys
import os
import time
import json
import urllib.request
from configparser import ConfigParser
from ghlicense import repobase
from ghlicense.providers import github, bitbucket, gitlab


def print_license_status(msg):
    """Print license status messages with a progress bar."""
    sys.stdout.write(" " * 52)
    sys.stdout.write("\r")
    sys.stdout.flush()
    print(msg)


def update_progress_bar(current, total):
    """Display a progressbar using ASCII characters alongwith the status."""
    sys.stdout.write("|")
    sys.stdout.write("#" * int(current * 40 / total))
    sys.stdout.write("-" * (40 - int(current * 40 / total)))
    sys.stdout.write(" | Done " + str(int(current * 100 / total)) + "% \r")
    sys.stdout.flush()


def update_license(url, name, badge):
    """Update the project with the specified License text and badge."""
    print(f"License {name} download in progress.")
    # If a file "LICENSE" does NOT exist in the repo
    if not os.path.isfile("LICENSE"):
        # Obtain the License text and save it as the file LICENSE
        urllib.request.urlretrieve(url, "LICENSE")
        print(f"License {name} saved as file LICENSE.")

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
            print(f"Added badge license for {name} in {readme_name}.")
            return readme_name

    return ""


def save_last_used_licenses(last_used_licenses):
    """
    Saves the most recently uses licenses in the config file. If no config
    file exists, it will create one.

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
    """
    Returns an array of the last used licenses, in order of
    most recently used first. Returns an empty array if no license has been
    previously used.
    """
    config = ConfigParser()
    if not config.read(os.path.expanduser("~/.gh-license/config.ini")):
        return []
    try:
        return config["lastUsed"]["lastUsedLicenses"].split(",")
    except KeyError:
        return []


def pick_license_from_last_used(last_used_licenses, licenses_path):
    """
    Assumes the user did not select a license. Presents them with
    their most recently used licenses from last_used_licenses and allows
    them to select one (or any other license).

    Returns the string name of the selected license.
    last_used_licenses: a sequence of the three most recently used licenses
    in order of most recently used first.
    """
    print("You have not selected a license, ", end="")
    if last_used_licenses:
        print("the last licenses you've used are: ")
        for i, license_name in enumerate(last_used_licenses):
            print(f"[{i+1}]{license_name}", end="")
            if i < len(last_used_licenses) - 1:
                print(", ", end="")
        print("\nPress [1], [2], and so on to download the license,\nor e", end="")
    else:
        print("you also have no previously used licenses.\n", end="")

    print("Enter the name of the license you want, or press " + "[n] to see a description of every license.")
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


def print_license_list(licenses_path):
    """Print the license list from the JSON file provided with the package"""
    try:
        with open(licenses_path, "r", encoding="UTF-8") as file:
            licenses_data = json.load(file)
        for _license in licenses_data:
            name = _license["name"]
            description = _license["description"]
            print(f"{name}")
            print(f"    {description}")
    except FileNotFoundError:
        sys.stderr.write("licenses.json file not found.\n")


def update_license_from_json(chosen_license, licenses_path):
    """Check if the license provided exists in the package otherwise proceed"""
    print("Updating license from JSON...")
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
        print(f"License found: {license_info['name']}")
        print("License update successful.")
        return update_license(license_info["link"], chosen_license, license_info["badge"])

    if isinstance(chosen_license, bool):
        print("No license provided")
    else:
        print(f"License {chosen_license} not found!")
    sys.exit(1)


def git_commit(ARGS, name, readme_name):
    """Git commit the readme file changed"""
    if os.path.isdir(".git") and os.path.exists("LICENSE"):
        os.system("git add LICENSE")
        os.system(f"git add {readme_name}")
        os.system(f"git commit -m 'Added {name} LICENSE'")
    # If within a git repository, commit the above changes to current branch
    # Verify which is the current branch
    try:
        # os.popen() runs the command and capture its output as a file-like object \
        # while read() will read the output of the command
        current_branch_bytes = os.popen("git rev-parse --abbrev-ref HEAD").read().encode("utf-8")
        # let's encode it and decode the UTF-8 bytes to a stringa \
        # and strip whitespaces to get the branch name
        current_branch = current_branch_bytes.decode("utf-8").strip()
        print(f"Current Git branch is: {current_branch}")
    except Exception as e:
        print(f"Error: {e}")

    # If a remote repository exists, attempt to push changes to it
    if ARGS.origin is not None:
        os.system(f"git push {ARGS.origin} {current_branch}")
    else:
        os.system(f"git push origin {current_branch}")


def args_scan(ARGS):
    """The scan command"""
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
        print(f' No report file name found, using default "{report_file_name}"')
    else:
        report_file_name = ARGS.report

    # Start scanning user's public repos
    with open(report_file_name, "w", encoding="UTF-8") as report_file:
        report_file.write("Last scan done on: " + time.strftime("%c") + "\n")
        report_file.write("Scan report of user: " + ARGS.scan + "\n\n")
        count_total = len(list(user.get_repos()))
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

        # For each repo found
        for repo in user.get_repos():
            print(repo.full_name)
            license_url = repo.raw_base_url
            repo_url = repo.repo_url
            update_progress_bar(count_current, count_total)
            to_print = ""

            # Look for a License file in the root directory fo the repo
            for license_file in license_files:
                missing = True
                try:
                    urllib.request.urlretrieve(license_url + license_file)
                except urllib.error.HTTPError as err:
                    if err.code == 404:
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
                    print(" ! Is a fork, check the original or create a PR!")
                    to_print += " ! Is a fork, check the original or create a PR!\n"
                    count_forked += 1
            count_current += 1
            to_print += "\n"

        # Update progress based on % of repos scanned
        print("|" + "#" * 40 + "| Done 100%")
        report_file.write(to_print)
        report_file.write("Statistics: \n")
        report_file.write(f"Repos with License: {count_license}\n")
        report_file.write(f"Repos without License: {count_no_license}\n")
        report_file.write(f"Repos without License and forked: {count_forked}\n")
        report_file.write(f"Total Repos: {count_no_license + count_license}\n")
        report_file.close()


def args_license(ARGS, licenses_path):
    """The license command"""
    last_used_licenses = load_last_used_licenses()

    # This will be the actual license if explicitly called with a license
    chosen_license = ARGS.license

    # Called without a license. List off the last used licenses and let user select.
    if not ARGS.license:
        chosen_license = pick_license_from_last_used(last_used_licenses, licenses_path)

    readme_name = update_license_from_json(chosen_license, licenses_path)
    git_commit(ARGS, chosen_license, readme_name)

    # Save the three most recently used licenses (remove duplicates, keep order)
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
