#!/usr/bin/env python3

import os
import shutil
import subprocess
from configparser import ConfigParser

from setuptools.command.develop import develop


class PostDevelopCommand(develop):
    def run(self):
        main_path = os.path.expanduser("~/.gh-license")

        git_templates_path = "{}/git-templates".format(main_path)
        git_hooks_path = "{}/hooks".format(git_templates_path)

        config_path = "{}/config.ini".format(main_path)

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
