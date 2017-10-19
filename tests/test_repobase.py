import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ghlicense import repobase

from unittest import TestCase, main

class TestRepobase(TestCase):
    def test_default_value_init(self):
        default_repo = repobase.Repo("name", "raw_url","repo_url")
        self.assertEqual(default_repo.default_branch,"master")
        self.assertFalse(default_repo.fork)

    def test_get_providers(self):
        enabled, disabled = repobase.get_providers()
        self.assertIn(["github","bitbucket"], enabled)

if __name__ == "__main__":
    main()
