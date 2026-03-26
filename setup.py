#!/usr/bin/python3

from setuptools import setup, find_packages
import os
import shutil
import subprocess
from configparser import ConfigParser
from setuptools.command.develop import develop

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class PostDevelopCommand(develop):
    def run(self):
        main_path = os.path.expanduser("~/.gh-license")

        git_templates_path = f"{main_path}/git-templates"
        git_hooks_path = f"{git_templates_path}/hooks"

        config_path = f"{main_path}/config.ini"

        # copy the hooks folder in our git template folder
        shutil.copytree("setup/hooks", git_hooks_path)

        get_config_arguments = ["git", "config",
                                "--global", "init.templatedir"]

        if not os.path.exists(config_path):
            # save the current init.templatedir git config if the user already
            # had a value set for this
            try:
                current_config = subprocess.check_output(get_config_arguments)

                config = ConfigParser()
                config.read(config_path)
                config.add_section("main")
                config.set("main", "templatedir",
                           current_config.decode("utf-8"))

                with open(config_path, "w") as config_file:
                    config.write(config_file)
            except subprocess.CalledProcessError:
                pass  # don't create the config file

        # set our own git template path for the init.templatedir config
        set_config_arguments = get_config_arguments + [git_templates_path]

        subprocess.call(set_config_arguments)

        develop.run(self)


setup(
    name="gh-license",
    version="0.3.0",
    author="Mte90",
    author_email="mte90net@gmail.com",
    url="https://github.com/Mte90/GH-License",
    install_requires=open(os.path.join(BASE_DIR, "requirements.txt")).readlines(),
    license="GPLv3",
    description="Scan github, bitbucket or other providers repositories for missing license files and add them",
    download_url='https://github.com/Mte90/GH-License/tarball/0.3.0',
    package_data={"ghlicense": ["*.json"]},
    packages=find_packages(exclude=["setup", "setup.*"]),
    entry_points={
        'console_scripts': [
            'gh-license=ghlicense.cmd:main'
        ]
    },
    cmdclass={
        'develop': PostDevelopCommand
    }
)
