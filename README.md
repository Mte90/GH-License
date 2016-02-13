#GitHub License
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)   

This script scan every repo of the user on GitHub for a license file or download a license in the folder.  

Remember without a license file your project is proprietary also if on GitHub!


##Install

    curl -sL https://raw.githubusercontent.com/Mte90/GH-License/master/install.sh | bash -


##Example

    gh-license --scan Mte90 

Example of output https://gist.github.com/Mte90/4c5ec76c94afa61983f8

    gh-license --license GPLv3 && git add LICENSE && git commit -m "missing license" && git push origin master