#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2017 Carlos Jenkins <carlos@jenkins.co.cr>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Small delegating Python script to allow multiple hooks in a git repository.

Usage:

Make your building system to create a symbolic link in the git hooks directory
to this script with the name of the hook you want to attend. For example,
``pre-commit``.

This hook will then execute, in alphabetic order, all executables files
(subhooks) found under a folder named after the hook type you're attending
suffixed with ``.d``. For example, ``pre-commit.d``.

For example:

```
.git/hooks/
|_ pre-commit
|_ pre-commit.d/
   |_ 01-cpp_coding_standard
   |_ 02-python_coding_standard
   |_ 03-something_else
```

https://gist.github.com/revolter/99ea1acd48ad7c2d898bca2bc58f37bc
"""

from sys import argv
from subprocess import Popen, PIPE
from os import access, listdir, X_OK
from os.path import isfile, isdir, abspath, normpath, dirname, join, basename, splitext


GIT_HOOKS = [
    'applypatch-msg',
    'commit-msg',
    'post-update',
    'pre-applypatch',
    'pre-commit',
    'prepare-commit-msg',
    'pre-push',
    'pre-rebase',
    'update',
]


def main():
    """
    Execute subhooks for the assigned hook type.
    """

    # Check multihooks facing what hook type
    hook_type = splitext(basename(__file__))[0]
    if hook_type not in GIT_HOOKS:
        exit(1)

    # Lookup for sub-hooks directory
    root = normpath(abspath(dirname(__file__)))
    hooks_dir = join(root, '{}.d'.format(hook_type))
    if not isdir(hooks_dir):
        exit(0)

    # Gather scripts to call
    files = [join(hooks_dir, f) for f in listdir(hooks_dir)]
    hooks = sorted(
        [h for h in files if isfile(h) and access(h, X_OK)]
    )
    if not hooks:
        exit(0)

    # Execute hooks
    for h in hooks:
        hook_id = '{}.d/{}'.format(hook_type, basename(h))

        proc = Popen([h] + argv[1:], stdout=PIPE, stderr=PIPE)
        stdout_raw, stderr_raw = proc.communicate()

        stdout = stdout_raw.decode('utf-8').strip()
        stderr = stderr_raw.decode('utf-8').strip()

        if stdout:
            print(stdout)
        if stderr:
            print(stderr)

        if proc.returncode != 0:
            exit(proc.returncode)


if __name__ == '__main__':
    main()
