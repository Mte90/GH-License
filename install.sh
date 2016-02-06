#!/usr/bin/bash

wget https://raw.githubusercontent.com/Mte90/GH-License/master/gh-license.py -O /usr/local/bin/gh-license
chmod +x /usr/local/bin/gh-license

pip3 install pygithub

echo 'gh-license script install use: gh-license'
