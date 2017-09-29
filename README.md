# GitHosting License
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/e6705b4282fd459da427e24649081510)](https://www.codacy.com/app/mte90net/GH-License?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Mte90/GH-License&amp;utm_campaign=Badge_Grade)

This script scans every repo of a user on GitHub, Bitbucket or other providers available for a license file, downloads a license to the project folder, and adds a license badge in the readme of the project.

Remember, without a license file your project is proprietary even if it is on GitHub!


## Install

```
pip3 install gh-license
```

In case of a git clone:

```
pip3 install -e ./folder-of-the-repo
```


## Example

    gh-license --scan Mte90

With this command you will get a report in a file called Mte90-github-license-report

    gh-license --scan Mte90 --provider bitbucket

With this command you will get a report in a file called Mte90-bitbucket-license-report

    gh-license --scan Mte90 --report my-report

With this command you will get a report in a file called my-report

    gh-license --licenselist

With this command will be showed the licenses avalaible

    gh-license --license GPLv3

With this command, a GPLv3 license will be downloaded, a shields will be added in the readme and if Git is available a commit will be added and the changes will be pushed to the repo.

    gh-license --license GPLv3 -- origin upstream

With this command the commit will be pushed on the upstream origin

[Example of output](https://gist.github.com/Mte90/4c5ec76c94afa61983f8)
