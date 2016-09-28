#!/usr/bin/python3

import sys
import urllib.request
import argparse
import os.path
from github import Github

parser = argparse.ArgumentParser()
parser.add_argument("--scan", help="Scan repo of the user", action="store_true")
parser.add_argument("--license", help="Download a license file", action="store_true")
parser.add_argument('args', nargs=argparse.REMAINDER)
args = parser.parse_args()

def downloadLicense(url, name, badge):
    if not os.path.isfile("LICENSE"):
        urllib.request.urlretrieve(url, "LICENSE")
        print('License ' + name + ' downloaded with filename LICENSE.')
        
    readme_files = ['README.md','README.txt','readme','README','readme.txt','readme.md']
    for readme_file in readme_files:
        if os.path.isfile(readme_file):
            f = open(readme_file, 'r+')
            text = [i for i in f.readlines()]
            f.seek(0)
            if text[0][0] == '#':
               f.write(text[0]) 
               text.pop(0)
            f.write('[![License]' + badge + "   \n")
            f.write("".join(text))
            f.close()
            print('Added badge license for ' + name + ' in ' + readme_file + '.')

if args.scan:
    if len(args.args) < 1:
         sys.stderr.write('  First parameter is missing: the nick on GitHub\n')
         sys.exit(1)

    g = Github()
    user = g.get_user(args.args[0])

    for repo in user.get_repos():
        print(repo.full_name)

        license_url = 'http://github.com/' + repo.full_name + '/blob/' + repo.default_branch + '/'
        license_files = ['LICENSE.txt','license','LICENSE','license.txt','license.md','LICENSE.md']
        for license_file in license_files:
            missing = True
            try:
                urllib.request.urlretrieve(license_url + license_file)
            except urllib.error.HTTPError as err:
                if err.code == 404:
                    missing = True
            else:
                print(' ✓ Found: ' + license_url + license_file)
                missing = False
                break

        if missing:
            print(' ✗ Missing the license, this repo is proprietary!')
            if repo.fork:
                print(' ☐ Is a fork, check the original or create a PR!')
elif args.license:
    if len(args.args) < 1:
         sys.stderr.write('  First parameter is missing: The license: GPLv2, GPLv3, LGPLv3, AGPLv3, FDLv1.3, Apachev2, CC-BY, BSDv2, BSDv3, BSDv4, MPLv2, UNLICENSE, MIT\n')
         sys.exit(1)

    if args.args[0] == 'GPLv2':
        downloadLicense("http://www.gnu.org/licenses/gpl-2.0.txt", args.args[0], '(https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://img.shields.io/badge/License-GPL%20v2-blue.svg)')
    elif args.args[0] == 'GPLv3':
        downloadLicense("http://www.gnu.org/licenses/gpl-3.0.txt", args.args[0], '(https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)')
    elif args.args[0] == 'LGPLv3':
        downloadLicense("http://www.gnu.org/licenses/lgpl-3.0.txt", args.args[0], '(https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](http://www.gnu.org/licenses/lgpl-3.0)')
    elif args.args[0] == 'AGPLv3':
        downloadLicense("http://www.gnu.org/licenses/agpl-3.0.txt", args.args[0], '(https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)')
    elif args.args[0] == 'FDLv1.3':
        downloadLicense("http://www.gnu.org/licenses/fdl-1.3.txt", args.args[0], '(https://img.shields.io/badge/License-FDL%20v1.3-blue.svg)](http://www.gnu.org/licenses/fdl-1.3)')
    elif args.args[0] == 'Apachev2':
        downloadLicense("http://www.opensource.apple.com/source/apache2/apache2-19/apache2.txt?txt", args.args[0], '(https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)')
    elif args.args[0] == 'CC-BY':
        downloadLicense("http://creativecommons.org/licenses/by/3.0/legalcode.txt", args.args[0], '(https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)(http://creativecommons.org/licenses/by/4.0/)')
    elif args.args[0] == 'BSDv2':
        downloadLicense("https://spdx.org/licenses/BSD-2-Clause.txt", args.args[0], '(https://img.shields.io/badge/License-BSD%20v2-blue.svg)](https://spdx.org/licenses/BSD-2-Clause)')
    elif args.args[0] == 'BSDv3':
        downloadLicense("https://spdx.org/licenses/BSD-3-Clause.txt", args.args[0], '(https://img.shields.io/badge/License-BSD%20v3-blue.svg)](https://spdx.org/licenses/BSD-3-Clause)')
    elif args.args[0] == 'BSDv4':
        downloadLicense("https://spdx.org/licenses/BSD-4-Clause.txt", args.args[0], '(https://img.shields.io/badge/License-BSD%20v4-blue.svg)](https://spdx.org/licenses/BSD-4-Clause)')
    elif args.args[0] == 'MPLv2':
        downloadLicense("https://www.mozilla.org/media/MPL/2.0/index.815ca599c9df.txt", args.args[0], '(https://img.shields.io/badge/License-MozillaPublicLicense%20v2-blue.svg)](https://www.mozilla.org/en-US/MPL/2.0)')
    elif args.args[0] == 'UNLICENSE':
        downloadLicense("http://unlicense.org/UNLICENSE", args.args[0], '(https://img.shields.io/badge/License-UNLICENSE%20v1-blue.svg)](http://unlicense.org/UNLICENSE)')
    elif args.args[0] == 'MIT':
        downloadLicense("https://spdx.org/licenses/MIT.txt", args.args[0], '(https://img.shields.io/badge/License-MIT%20v1-blue.svg)](https://spdx.org/licenses/MIT.html#licenseText)')
    else:
        print('License not found!')
else:
    print('  Remember without a license file your project is proprietary!')
    print('  GitHub License checker and downloader by Mte90')
    print('')
    print('  This script scan every repo of the user for a license file or')
    print('  download a license, choose on http://choosealicense.com/licenses/')
    print('  or use http://www.addalicense.com/ to add automatically')
    print('  on your GitHub repos')
    print('')
    print('Use --scan or --license command')
