#!/usr/bin/python3

from setuptools import setup, find_packages
from setup.setup_hook import PostDevelopCommand

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

setup(
    name="gh-license",
    version="0.2.7",
    author="Mte90",
    author_email="mte90net@gmail.com",
    url="https://github.com/Mte90/GH-License",
    install_requires=open(os.path.join(BASE_DIR, "requirements.txt")).readlines(),
    license="GPLv3",
    description="Scan github, bitbucket or other providers repositories for missing license files and add them",
    download_url='https://github.com/Mte90/GH-License/tarball/0.2.7',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gh-license=ghlicense.cmd:main'
        ]
    },
    cmdclass={
        'develop': PostDevelopCommand
    }
)
