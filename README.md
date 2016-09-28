#GitHub License
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)   

This script scan every repo of the user on GitHub for a license file or download a license (and add a license badge in the readme) in the folder.  

Remember without a license file your project is proprietary also if on GitHub!


##Install

    curl -sL https://raw.githubusercontent.com/Mte90/GH-License/master/install.sh | bash -


##Example

    gh-license --scan Mte90 

With this command you will get a report in a file Mte90-gh-license-report

    gh-license --license GPLv3

With this command will be downlaoded the license GPLv3, added a shields in the readme and if Git is avialable add a commit and pushed to the repo.

Example of output https://gist.github.com/Mte90/4c5ec76c94afa61983f8
