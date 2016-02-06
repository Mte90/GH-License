#!/usr/bin/python3

import sys
import urllib.request
import argparse
from github import Github

parser = argparse.ArgumentParser()
parser.add_argument("--scan", help="Scan repo of the user", action="store_true")
parser.add_argument("--license", help="Download a license file", action="store_true")
parser.add_argument('args', nargs=argparse.REMAINDER)
args = parser.parse_args()

def downloadLicense(url, name):
    urllib.request.urlretrieve(url, "LICENSE")
    print('License ' + name + ' downloaded with filename LICENSE.')

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
         sys.stderr.write('  First parameter is missing: The license: GPLv2, GPLv3, LGPLv3, AGPLv3, FDLv1.3, Apachev2, CC-BY\n')
         sys.exit(1)

    if args.args[0] == 'GPLv2':
        downloadLicense("http://www.gnu.org/licenses/gpl-2.0.txt", args.args[0])
    elif args.args[0] == 'GPLv3':
        downloadLicense("http://www.gnu.org/licenses/gpl-3.0.txt", args.args[0])
    elif args.args[0] == 'LGPLv3':
        downloadLicense("http://www.gnu.org/licenses/lgpl-3.0.txt", args.args[0])
    elif args.args[0] == 'AGPLv3':
        downloadLicense("http://www.gnu.org/licenses/agpl-3.0.txt", args.args[0])
    elif args.args[0] == 'FDLv1.3':
        downloadLicense("http://www.gnu.org/licenses/fdl-1.3.txt", args.args[0])
    elif args.args[0] == 'Apachev2':
        downloadLicense("http://www.opensource.apple.com/source/apache2/apache2-19/apache2.txt?txt", args.args[0])
    elif args.args[0] == 'CC-BY':
        downloadLicense("http://creativecommons.org/licenses/by/3.0/legalcode.txt", args.args[0])
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
