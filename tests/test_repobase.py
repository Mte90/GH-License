import os
import sys
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ghlicense import repobase
from unittest import TestCase, main

class TestRepobase(TestCase):
    def test_default_value_init(self):
        default_repo = repobase.Repo("name", "raw_url","repo_url")
        self.assertEqual(default_repo.default_branch,"master")
        self.assertFalse(default_repo.fork)

    def test_get_default_providers(self):
        enabled, disabled = repobase.get_providers()
        self.assertEqual(['github', 'bitbucket'], enabled)
        self.assertEqual([], disabled)

    @patch("ghlicense.repobase.PROVIDERS")
    def test_disable_all_provider(self, mock_providers):
        fake_dict = {"github": None, "bitbucket": True}
        mock_providers.__getitem__.side_effect = fake_dict.__getitem__
        enabled, disabled = repobase.get_providers()
        #self.assertEqual(["bitbucket"], enabled)
        self.assertEqual(["github"], disabled)

    def test_get_provider_exit_for_unknown_provider(self):
        with self.assertRaises(SystemExit):
            repobase.get_provider("unknown_provider")

    def test_get_provider_work_with_known_provider(self):
        provider = repobase.get_provider("github")
        self.assertEqual(repobase.PROVIDERS["github"],provider)

    def test_register_new_provider(self):
        repobase.register_provider("new_provider", None, True)
        enabled, disabled = repobase.get_providers()
        self.assertIn("new_provider", enabled)

    def test_cannot_register_no_loaded_provider(self):
        repobase.register_provider("new_provider", None, False)
        enabled, disabled = repobase.get_providers()
        self.assertNotIn("new_provider", enabled)



if __name__ == "__main__":
    main()
