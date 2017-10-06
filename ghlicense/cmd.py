#!/usr/bin/python3

# Import the necessary packages

import sys
import time
import urllib.request
import argparse
import os
from configparser import ConfigParser
from ghlicense import repobase
from ghlicense import providers
from argparse import RawTextHelpFormatter

enhanced_description = """
    This script scans every repo of the specified user for a license
    file. If a license can't be found, the script will upload a
    a specified license to your repo.\n
    Choose a license on http://choosealicense.com/licenses/ or use
    http://www.addalicense.com/.\n
    Remember, without a license file, your project is proprietary!
"""

# Load all the providers
enabled_providers, disabled_providers = repobase.get_providers()

# Parse the cmdline and initialise args
parser = argparse.ArgumentParser(description = "GitHosting License checker and downloader",
        epilog = enhanced_description, formatter_class=RawTextHelpFormatter)

err_providers_txt = "(errored providers: %s)" % ", ".join(disabled_providers) if len(disabled_providers) > 0 else ""

parser.add_argument("--scan", help="Scan repo of the user, arguments: [User_nick]", action="store")
parser.add_argument("--license", help="Download a license file, arguments: [License_name]", nargs='?', const=True)
parser.add_argument("--licenselist", help="Show licenses available", action="store_true")
parser.add_argument("--provider", help="Repository provider. Defaults to github. Available providers: %s %s" %
        (", ".join(enabled_providers), err_providers_txt), action="store", default="github")
parser.add_argument("--report", help="The report filename for scan (optional)", action="store")
parser.add_argument("--origin", help="The origin of the git repo (optional)", action="store")
parser.add_argument('args', nargs=argparse.REMAINDER)

args = parser.parse_args()

# Check whether atleast 1 cmdline param was passed to the script.
# If not then display help/usage and quit.
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(0)

def printLicenseStatus(x):
    """Print License status messages with a progressbar."""
    sys.stdout.write(" "*52)
    sys.stdout.write("\r")
    sys.stdout.flush()
    print (x)

def updateProgressBar(current, total):
    """Display a progressbar using ASCII characters alongwith the status."""
    sys.stdout.write("|")
    sys.stdout.write("#"*int(current*40/total))
    sys.stdout.write("-"*(40-int(current*40/total)))
    sys.stdout.write(" | Done " + str(int(current*100/total)) + "% \r")
    sys.stdout.flush()

def updateLicense(url, name, badge):
    """Update the project with the specified License text and badge."""

    print('License ' + name + ' download in progress.')
    # If a file "LICENSE" does NOT exist in the repo
    if not os.path.isfile("LICENSE"):
        # Obtain the License text and save it as the file LICENSE
        urllib.request.urlretrieve(url, "LICENSE")
        print('License ' + name + ' saved as file LICENSE.')

    # If a README file by any of these names exists
    # then add License details and badge to it.
    readme_files = ['README.md','Readme.md','README.txt','readme','README','readme.txt','readme.md', 'read_me', 'Read_me', 'READ_ME']
    for readme_file in readme_files:

        if os.path.isfile(readme_file):
            # Open the file for reading/writing
            f = open(readme_file, 'r+')

            # Load entire file as a list of lines
            text = [i for i in f.readlines()]

            # Insert the License name and badge at the beginning of the file
            f.seek(0)
            if len(text) > 0 and text[0][0] == '#':
                f.write(text[0])
                text.pop(0)
            f.write('[![License]' + badge + "   \n")
            f.write("".join(text))
            f.close()
            print('Added badge license for ' + name + ' in ' + readme_file + '.')

            # If within a git repository, commit the above changes to current branch
            if os.path.isdir('.git') and os.path.exists('LICENSE'):
                os.system('git add LICENSE')
                os.system('git add ' + readme_file)
                os.system('git commit -m "Added ' + name + ' LICENSE"')
                # If a remote repository exists attempt to push change to it
                if args.origin != None:
                    os.system('git push ' + args.origin + ' master')
                else:
                    os.system('git push origin master')

def saveLastUsedLicenses(lastUsedLicenses):
    """
    Saves the most recently uses licenses in the config file. If no config
    file exists, it will create one.

    lastUsedLicenses: a sequence of the three most recently used licenses
    in order of most recently used first.
    """
    config = ConfigParser()
    configFilePath = os.path.expanduser('~/.gh-license/config.ini')
    config.read(configFilePath)

    # make the dirs if necessary.
    if not os.path.exists(os.path.dirname(configFilePath)):
        os.makedirs(os.path.dirname(configFilePath))

    if not 'lastUsed' in config:
        config['lastUsed'] = {}
    config['lastUsed']['lastUsedLicenses'] = ",".join(lastUsedLicenses)
    with open(configFilePath, 'w') as configFile:
        config.write(configFile)

def loadLastUsedLicenses():
    """
    Returns an array of the last used licenses, in order of
    most recently used first. Returns an empty array if no license has been
    previously used.
    """
    config = ConfigParser()
    if not config.read(os.path.expanduser('~/.gh-license/config.ini')):
        return []
    try:
        lastUsed = config['lastUsed']['lastUsedLicenses'].split(',')
        return lastUsed
    except KeyError as e:
        return []

def pickLicenseFromLastUsed(lastUsedLicenses):
    """
    Assumes the user did not select a license. Presents them with
    their most recently used licenses from lastUsedLicenses and allows
    them to select one (or any other license).

    Returns the string name of the selected license.
    lastUsedLicenses: a sequence of the three most recently used licenses
    in order of most recently used first.
    """
    print("You have not selected a license, ", end='')
    if lastUsedLicenses:
        print("the last licenses you've used are: ")
        for i in range(len(lastUsedLicenses)):
            print('[{num}]{license}'.format(num=i+1, license=lastUsedLicenses[i]),end='')
            if i < len(lastUsedLicenses) - 1:
                print(', ',end='')
        print("\nPress [1], [2], and so on to download the license,\nor e", end='')
    else:
        print("you also have no previously used licenses.\nE", end='')

    print("nter the name of the license you want, or press [n] to see a description of every license.")
    licenseInput = input('')

    # Print the list and then exit
    if licenseInput.lower() == 'n':
        printLicenseList()
        sys.exit(1)

    # Return the name of the selected license if possible, or just return the input license
    try:
        selectedLicense = lastUsedLicenses[int(licenseInput) - 1]
        return selectedLicense
    except (ValueError, IndexError) as e:
        return licenseInput

def printLicenseList():
    """Print a hardcoded list of known Licenses"""
    sys.stderr.write('\n  GPLv2\n'\
            '\tYou may copy, distribute and modify the software.\n'\
            '\tAny modifications must also be made available under\n'\
            '\tthe GPL along with build & install instructions.'\
            '\n\n  GPLv3\n'\
            '\tSame of GPLv2 but easily integrable with other licenses.'\
            '\n\n  LGPLv3\n'\
            '\tThis license is mainly applied to libraries.\n'\
            '\tDerivatives works that use LGPL library can use other licenses.'\
            '\n\n  AGPLv3\n'\
            '\tThe AGPL license differs from the other GNU licenses in that it was\n'\
            '\tbuilt for network software, the AGPL is the GPL of the web.'\
            '\n\n  FDLv1.3\n'\
            '\tThis license is for a manual, textbook, or other\n'\
            '\tfunctional and useful document "free" in the sense of freedom.'\
            '\n\n  Apachev2\n'\
            '\tYou can do what you like with the software, as long as you include the\n'\
            '\trequired notices.'\
            '\n\n  CC-BY\n'\
            '\tThis is the ‘standard’ creative commons.\n'\
            '\tIt should not be used for the software.'\
            '\n\n  BSDv2\n'\
            '\tThe BSD 2-clause license allows you almost unlimited freedom.'
            '\n\n  BSDv3\n'\
            '\tThe BSD 3-clause license allows you almost unlimited freedom.'
            '\n\n  BSDv4\n'\
            '\tThe BSD 4-clause license is a permissive license with a special \n'\
            '\tobligation to credit the copyright holders of the software.'\
            '\n\n  MPLv2\n'\
            '\tMPL is a copyleft license. You must make the source code for any\n'\
            '\tof your changes available under MPL, but you can combine the\n'\
            '\tMPL software with proprietary code.'\
            '\n\n  UNLICENSE\n'\
            '\tReleases code into the public domain.'\
            '\n\n  MIT\n'\
            '\tA short, permissive software license.\n\n')

# Execute the script
def main():

    # If the script was launched in "scan" mode
    if args.scan:

        # Initialise specified repo provider
        # (or use the default provider, if one is not specified)
        repo_provider = repobase.get_provider(args.provider)

        # Obtain the username passed on the cmd-line in "scan" mode
        user = repo_provider(args.scan)

        # Create the specified license report file
        # (or use the default license report file name, if one is not specified)
        if args.report == None:
            report_file = open(args.scan + '-' + args.provider + '-license-report','w')
            print(' No report file name found, using default "'+ args.scan + '-' + args.provider + '-license-report"!')
        else:
            report_file = open(args.report,'w')

        # Start scanning user's public repos
        report_file.write('Last scan done on: ' + time.strftime("%c") + "\n")
        report_file.write('Scan report of user: ' + args.scan + "\n\n")
        count_total = len(list(user.get_repos()))
        count_current = 0
        count_license = 0
        count_no_license = 0
        count_forked = 0

        # For each repo found
        for repo in user.get_repos():
            print(repo.full_name)
            license_url = repo.raw_base_url
            license_files = ['LICENSE.txt','license','LICENSE','license.txt','license.md','LICENSE.md']
            repo_url = repo.repo_url
            updateProgressBar(count_current, count_total)

            # Look for a License file in the root directory fo the repo
            for license_file in license_files:
                missing = True
                try:
                    urllib.request.urlretrieve(license_url + license_file)
                except urllib.error.HTTPError as err:
                    if err.code == 404:
                        missing = True
                else:
                    printLicenseStatus(' ✓ Found: ' + license_url + license_file)
                    report_file.write('Repo: ' + repo.full_name + "\nURL: " + repo_url + " \n")
                    report_file.write(' ✓ Found: ' + license_url + license_file + " \n")
                    missing = False
                    count_license+=1
                    break

            if missing:
                printLicenseStatus(' ✗ Missing the license, this repo is proprietary!')
                report_file.write('Repo: ' + repo.full_name + "\nURL: " + repo_url + " \n")
                report_file.write(' ✗ Missing the license, this repo is proprietary!\n')
                count_no_license+=1
                if repo.fork:
                    print(' ☐ Is a fork, check the original or create a PR!')
                    report_file.write(' ☐ Is a fork, check the original or create a PR!\n')
                    count_forked+=1
            count_current+=1
            report_file.write("\n")

        # Update progress based on % of repos scanned
        print ("|" + "#"*40 + "| Done 100%")
        report_file.write("Statistics: \n")
        report_file.write("Repos with License: " + str(count_license) + "\n")
        report_file.write("Repos without License: " + str(count_no_license) + "\n")
        report_file.write("Repos without License and forked: " + str(count_forked) + "\n")
        report_file.write("Total Repos: " + str(count_no_license + count_license) + "\n")
        report_file.close()

    # If the script was launched in "licenselist" mode
    elif args.licenselist == True:
        printLicenseList()
        sys.exit(1)

    # If the script was launched in "license" mode
    elif args.license:

        lastUsedLicenses = loadLastUsedLicenses()

        # This will be the actual license if explicitly called with a license
        chosenLicense = args.license

        # Called without a license. List off the last used licenses and let user select.
        if args.license == True:
            chosenLicense = pickLicenseFromLastUsed(lastUsedLicenses)

        # Check which license is being requested and update accordingly
        if chosenLicense == 'GPLv2':
            updateLicense("http://www.gnu.org/licenses/gpl-2.0.txt", chosenLicense, '(https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://img.shields.io/badge/License-GPL%20v2-blue.svg)')
        elif chosenLicense == 'GPLv3':
            updateLicense("http://www.gnu.org/licenses/gpl-3.0.txt", chosenLicense, '(https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)')
        elif chosenLicense == 'LGPLv3':
            updateLicense("http://www.gnu.org/licenses/lgpl-3.0.txt", chosenLicense, '(https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](http://www.gnu.org/licenses/lgpl-3.0)')
        elif chosenLicense == 'AGPLv3':
            updateLicense("http://www.gnu.org/licenses/agpl-3.0.txt", chosenLicense, '(https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)')
        elif chosenLicense == 'FDLv1.3':
            updateLicense("http://www.gnu.org/licenses/fdl-1.3.txt", chosenLicense, '(https://img.shields.io/badge/License-FDL%20v1.3-blue.svg)](http://www.gnu.org/licenses/fdl-1.3)')
        elif chosenLicense == 'Apachev2':
            updateLicense("http://www.opensource.apple.com/source/apache2/apache2-19/apache2.txt?txt", chosenLicense, '(https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)')
        elif chosenLicense == 'CC-BY':
            updateLicense("http://creativecommons.org/licenses/by/3.0/legalcode.txt", chosenLicense, '(https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)(http://creativecommons.org/licenses/by/4.0/)')
        elif chosenLicense == 'BSDv2':
            updateLicense("https://spdx.org/licenses/BSD-2-Clause.txt", chosenLicense, '(https://img.shields.io/badge/License-BSD%20v2-blue.svg)](https://spdx.org/licenses/BSD-2-Clause)')
        elif chosenLicense == 'BSDv3':
            updateLicense("https://spdx.org/licenses/BSD-3-Clause.txt", chosenLicense, '(https://img.shields.io/badge/License-BSD%20v3-blue.svg)](https://spdx.org/licenses/BSD-3-Clause)')
        elif chosenLicense == 'BSDv4':
            updateLicense("https://spdx.org/licenses/BSD-4-Clause.txt", chosenLicense, '(https://img.shields.io/badge/License-BSD%20v4-blue.svg)](https://spdx.org/licenses/BSD-4-Clause)')
        elif chosenLicense == 'MPLv2':
            updateLicense("https://www.mozilla.org/media/MPL/2.0/index.815ca599c9df.txt", chosenLicense, '(https://img.shields.io/badge/License-MozillaPublicLicense%20v2-blue.svg)](https://www.mozilla.org/en-US/MPL/2.0)')
        elif chosenLicense == 'UNLICENSE':
            updateLicense("http://unlicense.org/UNLICENSE", chosenLicense, '(https://img.shields.io/badge/License-UNLICENSE%20v1-blue.svg)](http://unlicense.org/UNLICENSE)')
        elif chosenLicense == 'MIT':
            updateLicense("https://spdx.org/licenses/MIT.txt", chosenLicense, '(https://img.shields.io/badge/License-MIT%20v1-blue.svg)](https://spdx.org/licenses/MIT.html#licenseText)')
        else:
            print('License {license} not found!'.format(license=chosenLicense))
            sys.exit(1)

        # Save the three most recently used licenses (remove duplicates, keep order)
        lastUsedLicenses.insert(0, chosenLicense)
        uniqueLastUsed = []
        [uniqueLastUsed.append(item) for item in lastUsedLicenses if item not in uniqueLastUsed]
        saveLastUsedLicenses(uniqueLastUsed[0:3])

if __name__ == "__main__":
    main()
