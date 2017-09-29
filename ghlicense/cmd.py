#!/usr/bin/python3

#Import the necessary packages

import sys
import time
import urllib.request
import argparse
import os
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

# Set all the  argument
parser = argparse.ArgumentParser(description = "GitHosting License checker and downloader",
    epilog = enhanced_description, formatter_class=RawTextHelpFormatter)

err_providers_txt = "(errored providers: %s)" % ", ".join(disabled_providers) if len(disabled_providers) > 0 else ""

parser.add_argument("--scan", help="Scan repo of the user, arguments: [User_nick]", action="store")

parser.add_argument("--license", help="Download a license file, arguments: [License_name]", action="store")

parser.add_argument("--licenselist", help="Show licenses available", action="store_true")

parser.add_argument("--provider", help="Repository provider. Defaults to github. Available providers: %s %s" % 
    (", ".join(enabled_providers), err_providers_txt), action="store", default="github")
    
parser.add_argument("--report", help="The report filename for scan (optional)", action="store")

parser.add_argument("--origin", help="The origin of the git repo (optional)", action="store")

parser.add_argument('args', nargs=argparse.REMAINDER)

args = parser.parse_args()

# In case of not parameter show the help
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(0)
    
# Used to print with the progressbar support
def makeprint(x):
    sys.stdout.write(" "*52)
    sys.stdout.write("\r")
    sys.stdout.flush()
    print (x)
    
# Generate a progressbar of the status
def progressBar(current, total):
    sys.stdout.write("|")
    sys.stdout.write("#"*int(current*40/total))
    sys.stdout.write("-"*(40-int(current*40/total)))
    sys.stdout.write(" | Done " + str(int(current*100/total)) + "% \r")
    sys.stdout.flush()
    
# Download the license
def downloadLicense(url, name, badge):
    print('License ' + name + ' download in progress.')    
    if not os.path.isfile("LICENSE"):
        urllib.request.urlretrieve(url, "LICENSE")
        print('License ' + name + ' downloaded with filename LICENSE.')
        
    # Search for the readme
    readme_files = ['README.md','Readme.md','README.txt','readme','README','readme.txt','readme.md', 'read_me', 'Read_me', 'READ_ME']
    for readme_file in readme_files:
        if os.path.isfile(readme_file):
            f = open(readme_file, 'r+')
            text = [i for i in f.readlines()]
            f.seek(0)
            if len(text) > 0 and text[0][0] == '#':
                f.write(text[0])
                text.pop(0)
            f.write('[![License]' + badge + "   \n")
            f.write("".join(text))
            f.close()
            print('Added badge license for ' + name + ' in ' + readme_file + '.')
            
            # In case of git commit the file
            if os.path.isdir('.git') and os.path.exists('LICENSE'):
                os.system('git add LICENSE')
                os.system('git add ' + readme_file)
                os.system("git commit -m 'missing LICENSE'")
                if args.origin != None:
                    os.system('git push ' + args.origin + ' master')
                else:
                    os.system('git push origin master')
                    
# Execute the script
def main():
    if args.scan:
        repo_provider = repobase.get_provider(args.provider)
        user = repo_provider(args.scan)
        if args.report == None:
            report_file = open(args.scan + '-' + args.provider + '-license-report','w')
            print(' No report file name found, using default "'+ args.scan + '-' + args.provider + '-license-report"!')
        else:
            report_file = open(args.report,'w')
        report_file.write('Last scan done on: ' + time.strftime("%c") + "\n")
        report_file.write('Scan report of user: ' + args.scan + "\n\n")
        count_total = len(list(user.get_repos()))
        count_current = 0
        count_license = 0
        count_no_license = 0
        count_forked = 0
        for repo in user.get_repos():
            print(repo.full_name)
            license_url = repo.raw_base_url
            license_files = ['LICENSE.txt','license','LICENSE','license.txt','license.md','LICENSE.md']
            repo_url = repo.repo_url
            progressBar(count_current, count_total)
            for license_file in license_files:
                missing = True
                try:
                    urllib.request.urlretrieve(license_url + license_file)
                except urllib.error.HTTPError as err:
                    if err.code == 404:
                        missing = True
                else:
                    makeprint(' ✓ Found: ' + license_url + license_file)
                    report_file.write('Repo: ' + repo.full_name + "\nURL: " + repo_url + " \n")
                    report_file.write(' ✓ Found: ' + license_url + license_file + " \n")
                    missing = False
                    count_license+=1
                    break

            if missing:
                makeprint(' ✗ Missing the license, this repo is proprietary!')
                report_file.write('Repo: ' + repo.full_name + "\nURL: " + repo_url + " \n")
                report_file.write(' ✗ Missing the license, this repo is proprietary!\n')
                count_no_license+=1
                if repo.fork:
                    print(' ☐ Is a fork, check the original or create a PR!')
                    report_file.write(' ☐ Is a fork, check the original or create a PR!\n')
                    count_forked+=1
            count_current+=1
            report_file.write("\n")
        print ("|" + "#"*40 + "| Done 100%")
        report_file.write("Statistics: \n")
        report_file.write("Repos with License: " + str(count_license) + "\n")
        report_file.write("Repos without License: " + str(count_no_license) + "\n")
        report_file.write("Repos without License and forked: " + str(count_forked) + "\n")
        report_file.write("Total Repos: " + str(count_no_license + count_license) + "\n")
        report_file.close()

    elif args.licenselist == True:
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
             sys.exit(1)
             
    elif args.license:
        if args.license == 'GPLv2':
            downloadLicense("http://www.gnu.org/licenses/gpl-2.0.txt", args.license, '(https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://img.shields.io/badge/License-GPL%20v2-blue.svg)')
        elif args.license == 'GPLv3':
            downloadLicense("http://www.gnu.org/licenses/gpl-3.0.txt", args.license, '(https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)')
        elif args.license == 'LGPLv3':
            downloadLicense("http://www.gnu.org/licenses/lgpl-3.0.txt", args.license, '(https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](http://www.gnu.org/licenses/lgpl-3.0)')
        elif args.license == 'AGPLv3':
            downloadLicense("http://www.gnu.org/licenses/agpl-3.0.txt", args.license, '(https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)')
        elif args.license == 'FDLv1.3':
            downloadLicense("http://www.gnu.org/licenses/fdl-1.3.txt", args.license, '(https://img.shields.io/badge/License-FDL%20v1.3-blue.svg)](http://www.gnu.org/licenses/fdl-1.3)')
        elif args.license == 'Apachev2':
            downloadLicense("http://www.opensource.apple.com/source/apache2/apache2-19/apache2.txt?txt", args.license, '(https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)')
        elif args.license == 'CC-BY':
            downloadLicense("http://creativecommons.org/licenses/by/3.0/legalcode.txt", args.license, '(https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)(http://creativecommons.org/licenses/by/4.0/)')
        elif args.license == 'BSDv2':
            downloadLicense("https://spdx.org/licenses/BSD-2-Clause.txt", args.license, '(https://img.shields.io/badge/License-BSD%20v2-blue.svg)](https://spdx.org/licenses/BSD-2-Clause)')
        elif args.license == 'BSDv3':
            downloadLicense("https://spdx.org/licenses/BSD-3-Clause.txt", args.license, '(https://img.shields.io/badge/License-BSD%20v3-blue.svg)](https://spdx.org/licenses/BSD-3-Clause)')
        elif args.license == 'BSDv4':
            downloadLicense("https://spdx.org/licenses/BSD-4-Clause.txt", args.license, '(https://img.shields.io/badge/License-BSD%20v4-blue.svg)](https://spdx.org/licenses/BSD-4-Clause)')
        elif args.license == 'MPLv2':
            downloadLicense("https://www.mozilla.org/media/MPL/2.0/index.815ca599c9df.txt", args.license, '(https://img.shields.io/badge/License-MozillaPublicLicense%20v2-blue.svg)](https://www.mozilla.org/en-US/MPL/2.0)')
        elif args.license == 'UNLICENSE':
            downloadLicense("http://unlicense.org/UNLICENSE", args.license, '(https://img.shields.io/badge/License-UNLICENSE%20v1-blue.svg)](http://unlicense.org/UNLICENSE)')
        elif args.license == 'MIT':
            downloadLicense("https://spdx.org/licenses/MIT.txt", args.license, '(https://img.shields.io/badge/License-MIT%20v1-blue.svg)](https://spdx.org/licenses/MIT.html#licenseText)')
        else:
            print('License not found!')    

if __name__ == "__main__":
    main()
