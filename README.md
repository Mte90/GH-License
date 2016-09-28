#GitHub License
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)   

This script scans every repo of a user on GitHub for a license file, downloads a license to the project folder, and adds a license badge in the readme of the project.

Remember, without a license file your project is proprietary even if it is on GitHub!


##Install

    curl -sL https://raw.githubusercontent.com/Mte90/GH-License/master/install.sh | bash -


##Example

    gh-license --scan Mte90

With this command you will get a report in a file called Mte90-gh-license-report

    gh-license --license GPLv3

With this command, a GPLv3 license will be downloaded, a shields will be added in the readme and if Git is available a commit will be added and the changes will be pushed to the repo.

Example of output https://gist.github.com/Mte90/4c5ec76c94afa61983f8
