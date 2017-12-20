#!/usr/bin/env python3

import os
import sys
import time
import urllib.request
from argparse import REMAINDER, ArgumentParser, RawTextHelpFormatter
from configparser import ConfigParser

from ghlicense import repobase
from ghlicense.providers import *

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
    epilog=ENHANCED_DESCRIPTION, formatter_class=RawTextHelpFormatter)

ERR_PROVIDERS_TXT = "(errored providers: %s)" % ", ".join(
    DISABLED_PROVIDERS) if DISABLED_PROVIDERS else ""

PARSER.add_argument(
    "--scan", help="Scan repo of the user, arguments: [User_nick]", action="store")
PARSER.add_argument(
    "--license", help="Download a license file, arguments: [License_name]", nargs='?', const=True)
PARSER.add_argument(
    "--licenselist", help="Show licenses available", action="store_true")
PARSER.add_argument("--provider",
                    help="Repository provider. Defaults to github. Available providers: %s %s" %
                    (", ".join(ENABLED_PROVIDERS), ERR_PROVIDERS_TXT),
                    action="store", default="github")
PARSER.add_argument(
    "--report", help="The report filename for scan (optional)", action="store")
PARSER.add_argument(
    "--origin", help="The origin of the git repo (optional)", action="store")
PARSER.add_argument('args', nargs=REMAINDER)

ARGS = PARSER.parse_args()

# Check whether at least 1 cmdline param was passed to the script.
# If not then display help/usage and quit.
if len(sys.argv) < 2:
    PARSER.print_help()
    sys.exit(0)


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

    print('License ' + name + ' download in progress.')
    # If a file "LICENSE" does NOT exist in the repo
    if not os.path.isfile("LICENSE"):
        # Obtain the License text and save it as the file LICENSE
        urllib.request.urlretrieve(url, "LICENSE")
        print('License ' + name + ' saved as file LICENSE.')

    # If a README file by any of these names exists
    # then add License details and badge to it.
    readme_names = ['README.md', 'Readme.md', 'README.txt', 'readme',
                    'README', 'readme.txt', 'readme.md', 'read_me', 'Read_me',
                    'READ_ME']
    for readme_name in readme_names:

        if os.path.isfile(readme_name):
            # Open the file for reading/writing
            readme_file = open(readme_name, 'r+')

            # Load entire file as a list of lines
            text = [i for i in readme_file.readlines()]

            # Insert the License name and badge at the beginning of the file
            readme_file.seek(0)
            if text and text[0][0] == '#':
                readme_file.write(text[0])
                text.pop(0)
            readme_file.write('[![License]' + badge + "   \n")
            readme_file.write("".join(text))
            readme_file.close()
            print('Added badge license for ' +
                  name + ' in ' + readme_name + '.')

            # If within a git repository, commit the above changes to current branch
            if os.path.isdir('.git') and os.path.exists('LICENSE'):
                os.system('git add LICENSE')
                os.system('git add ' + readme_name)
                os.system('git commit -m "Added ' + name + ' LICENSE"')
                # If a remote repository exists attempt to push change to it
                if ARGS.origin != None:
                    os.system('git push ' + ARGS.origin + ' master')
                else:
                    os.system('git push origin master')


def save_last_used_licenses(last_used_licenses):
    """
    Saves the most recently uses licenses in the config file. If no config
    file exists, it will create one.

    last_used_licenses: a sequence of the three most recently used licenses
    in order of most recently used first.
    """
    config = ConfigParser()
    config_file_path = os.path.expanduser('~/.gh-license/config.ini')
    config.read(config_file_path)

    # make the dirs if necessary.
    if not os.path.exists(os.path.dirname(config_file_path)):
        os.makedirs(os.path.dirname(config_file_path))

    if 'lastUsed' not in config:
        config['lastUsed'] = {}
    config['lastUsed']['lastUsedLicenses'] = ",".join(last_used_licenses)
    with open(config_file_path, 'w') as config_file:
        config.write(config_file)


def load_last_used_licenses():
    """
    Returns an array of the last used licenses, in order of
    most recently used first. Returns an empty array if no license has been
    previously used.
    """
    config = ConfigParser()
    if not config.read(os.path.expanduser('~/.gh-license/config.ini')):
        return []
    try:
        return config['lastUsed']['lastUsedLicenses'].split(',')
    except KeyError:
        return []


def pick_license_from_last_used(last_used_licenses):
    """
    Assumes the user did not select a license. Presents them with
    their most recently used licenses from last_used_licenses and allows
    them to select one (or any other license).

    Returns the string name of the selected license.
    last_used_licenses: a sequence of the three most recently used licenses
    in order of most recently used first.
    """
    print("You have not selected a license, ", end='')
    if last_used_licenses:
        print("the last licenses you've used are: ")
        for i, license_name in enumerate(last_used_licenses):
            print('[{num}]{license}'.format(
                num=i + 1, license=license_name), end='')
            if i < len(last_used_licenses) - 1:
                print(', ', end='')
        print(
            "\nPress [1], [2], and so on to download the license,\nor e", end='')
    else:
        print("you also have no previously used licenses.\n", end='')

    print("Enter the name of the license you want, or press " +
          "[n] to see a description of every license.")
    license_input = input('')

    # Print the list and then exit
    if license_input.lower() == 'n':
        print_license_list()
        sys.exit(1)

    # Return the name of the selected license if possible, or just return the input license
    try:
        selected_license = last_used_licenses[int(license_input) - 1]
        return selected_license
    except (ValueError, IndexError):
        return license_input


def print_license_list():
    """Print a hardcoded list of known Licenses"""
    sys.stderr.write('\n  GPLv2\n'
                     '\tYou may copy, distribute and modify the software.\n'
                     '\tAny modifications must also be made available under\n'
                     '\tthe GPL along with build & install instructions.'
                     '\n\n  GPLv3\n'
                     '\tSame of GPLv2 but easily integrable with other licenses.'
                     '\n\n  LGPLv3\n'
                     '\tThis license is mainly applied to libraries.\n'
                     '\tDerivatives works that use LGPL library can use other licenses.'
                     '\n\n  AGPLv3\n'
                     '\tThe AGPL license differs from the other GNU licenses in that it was\n'
                     '\tbuilt for network software, the AGPL is the GPL of the web.'
                     '\n\n  FDLv1.3\n'
                     '\tThis license is for a manual, textbook, or other\n'
                     '\tfunctional and useful document "free" in the sense of freedom.'
                     '\n\n  Apachev2\n'
                     '\tYou can do what you like with the software, as long as you include the\n'
                     '\trequired notices.'
                     '\n\n  CC-BY\n'
                     '\tThis is the ‘standard’ creative commons.\n'
                     '\tIt should not be used for the software.'
                     '\n\n  BSDv2\n'
                     '\tThe BSD 2-clause license allows you almost unlimited freedom.'
                     '\n\n  BSDv3\n'
                     '\tThe BSD 3-clause license allows you almost unlimited freedom.'
                     '\n\n  BSDv4\n'
                     '\tThe BSD 4-clause license is a permissive license with a special \n'
                     '\tobligation to credit the copyright holders of the software.'
                     '\n\n  MPLv2\n'
                     '\tMPL is a copyleft license. You must make the source code for any\n'
                     '\tof your changes available under MPL, but you can combine the\n'
                     '\tMPL software with proprietary code.'
                     '\n\n  UNLICENSE\n'
                     '\tReleases code into the public domain.'
                     '\n\n  MIT\n'
                     '\tA short, permissive software license.'
                     '\n\n  EUPL\n'
                     '\tThe “European Union Public Licence” (EUPL) The EUPL is the first\n'
                     '\tEuropean Free/Open Source Software (F/OSS) licence. It has been\n'
                     '\tcreated on the initiative of the European Commission.\n\n')


def main():
    """Execute the script."""

    # If the script was launched in "scan" mode
    if ARGS.scan:

        # Initialise specified repo provider
        # (or use the default provider, if one is not specified)
        repo_provider = repobase.get_provider(ARGS.provider)

        # Obtain the username passed on the cmd-line in "scan" mode
        user = repo_provider(ARGS.scan)

        # Create the specified license report file
        # (or use the default license report file name, if one is not specified)
        if ARGS.report is None:
            report_file = open(ARGS.scan + '-' +
                               ARGS.provider + '-license-report', 'w')
            print(' No report file name found, using default "' +
                  ARGS.scan + '-' + ARGS.provider + '-license-report"!')
        else:
            report_file = open(ARGS.report, 'w')

        # Start scanning user's public repos
        report_file.write('Last scan done on: ' + time.strftime("%c") + "\n")
        report_file.write('Scan report of user: ' + ARGS.scan + "\n\n")
        count_total = len(list(user.get_repos()))
        count_current = 0
        count_license = 0
        count_no_license = 0
        count_forked = 0

        license_base_name = 'license'
        # This is ordered by the most common extensions
        license_extensions = ['', '.md', '.txt']
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

            # Look for a License file in the root directory fo the repo
            for license_file in license_files:
                missing = True
                try:
                    urllib.request.urlretrieve(license_url + license_file)
                except urllib.error.HTTPError as err:
                    if err.code == 404:
                        missing = True
                else:
                    print_license_status(
                        ' ✓ Found: ' + license_url + license_file)
                    report_file.write(
                        'Repo: ' + repo.full_name + "\nURL: " + repo_url + " \n")
                    report_file.write(
                        ' ✓ Found: ' + license_url + license_file + " \n")
                    missing = False
                    count_license += 1
                    break

            if missing:
                print_license_status(
                    ' ✗ Missing the license, this repo is proprietary!')
                report_file.write('Repo: ' + repo.full_name +
                                  "\nURL: " + repo_url + " \n")
                report_file.write(
                    ' ✗ Missing the license, this repo is proprietary!\n')
                count_no_license += 1
                if repo.fork:
                    print(' ! Is a fork, check the original or create a PR!')
                    report_file.write(' ! Is a fork, check the original or create a PR!\n')
                    count_forked+=1
            count_current+=1
            report_file.write("\n")

        # Update progress based on % of repos scanned
        print("|" + "#" * 40 + "| Done 100%")
        report_file.write("Statistics: \n")
        report_file.write("Repos with License: " + str(count_license) + "\n")
        report_file.write("Repos without License: " +
                          str(count_no_license) + "\n")
        report_file.write(
            "Repos without License and forked: " + str(count_forked) + "\n")
        report_file.write("Total Repos: " +
                          str(count_no_license + count_license) + "\n")
        report_file.close()

    # If the script was launched in "licenselist" mode
    elif ARGS.licenselist:
        print_license_list()
        sys.exit(1)

    # If the script was launched in "license" mode
    elif ARGS.license:

        last_used_licenses = load_last_used_licenses()

        # This will be the actual license if explicitly called with a license
        chosen_license = ARGS.license

        # Called without a license. List off the last used licenses and let user select.
        if not ARGS.license:
            chosen_license = pick_license_from_last_used(last_used_licenses)

        # Check which license is being requested and update accordingly
        if chosen_license == 'GPLv2':
            update_license("http://www.gnu.org/licenses/gpl-2.0.txt", chosen_license,
                           '(https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://img.shields.io/badge/License-GPL%20v2-blue.svg)')
        elif chosen_license == 'GPLv3':
            update_license("http://www.gnu.org/licenses/gpl-3.0.txt", chosen_license,
                           '(https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)')
        elif chosen_license == 'LGPLv3':
            update_license("http://www.gnu.org/licenses/lgpl-3.0.txt", chosen_license,
                           '(https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](http://www.gnu.org/licenses/lgpl-3.0)')
        elif chosen_license == 'AGPLv3':
            update_license("http://www.gnu.org/licenses/agpl-3.0.txt", chosen_license,
                           '(https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)')
        elif chosen_license == 'FDLv1.3':
            update_license("http://www.gnu.org/licenses/fdl-1.3.txt", chosen_license,
                           '(https://img.shields.io/badge/License-FDL%20v1.3-blue.svg)](http://www.gnu.org/licenses/fdl-1.3)')
        elif chosen_license == 'Apachev2':
            update_license("http://www.opensource.apple.com/source/apache2/apache2-19/apache2.txt?txt", chosen_license,
                           '(https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)')
        elif chosen_license == 'CC-BY':
            update_license("http://creativecommons.org/licenses/by/3.0/legalcode.txt", chosen_license,
                           '(https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)(http://creativecommons.org/licenses/by/4.0/)')
        elif chosen_license == 'BSDv2':
            update_license("https://spdx.org/licenses/BSD-2-Clause.txt", chosen_license,
                           '(https://img.shields.io/badge/License-BSD%20v2-blue.svg)](https://spdx.org/licenses/BSD-2-Clause)')
        elif chosen_license == 'BSDv3':
            update_license("https://spdx.org/licenses/BSD-3-Clause.txt", chosen_license,
                           '(https://img.shields.io/badge/License-BSD%20v3-blue.svg)](https://spdx.org/licenses/BSD-3-Clause)')
        elif chosen_license == 'BSDv4':
            update_license("https://spdx.org/licenses/BSD-4-Clause.txt", chosen_license,
                           '(https://img.shields.io/badge/License-BSD%20v4-blue.svg)](https://spdx.org/licenses/BSD-4-Clause)')
        elif chosen_license == 'MPLv2':
            update_license("https://www.mozilla.org/media/MPL/2.0/index.815ca599c9df.txt", chosen_license,
                           '(https://img.shields.io/badge/License-MozillaPublicLicense%20v2-blue.svg)](https://www.mozilla.org/en-US/MPL/2.0)')
        elif chosen_license == 'UNLICENSE':
            update_license("http://unlicense.org/UNLICENSE", chosen_license,
                           '(https://img.shields.io/badge/License-UNLICENSE%20v1-blue.svg)](http://unlicense.org/UNLICENSE)')
        elif chosen_license == 'MIT':
            update_license("https://spdx.org/licenses/MIT.txt", chosen_license,
                           '(https://img.shields.io/badge/License-MIT%20v1-blue.svg)](https://spdx.org/licenses/MIT.html#licenseText)')
        elif chosen_license == 'EUPL':
            update_license("https://joinup.ec.europa.eu/sites/default/files/inline-files/EUPL%20v1_2%20EN(1).txt", chosen_license,
                           '(https://img.shields.io/badge/License-EUPL%20v1.1-blue.svg)](https://joinup.ec.europa.eu/page/eupl-guidelines-faq-infographics)')
        else:
            print('License {license} not found!'.format(license=chosen_license))
            sys.exit(1)

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


if __name__ == "__main__":
    main()
