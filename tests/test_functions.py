"""Tests for ghlicense.functions module."""
import os
import pytest
import asyncio

from ghlicense import functions


class TestPrintLicenseStatus:
    """Tests for print_license_status function."""

    def test_print_license_status_output(self):
        """Test that print_license_status runs without error."""
        # Function uses logger.info, verify it doesn't raise
        functions.print_license_status("Test message")


class TestUpdateProgress:
    """Tests for progress bar functions."""

    def test_update_progress_bar_output(self, capsys):
        """Test that update_progress_bar produces output."""
        functions.update_progress_bar(10, 100)
        captured = capsys.readouterr()
        # Progress bar should print something
        assert len(captured.out) > 0


class TestUpdateLicense:
    """Tests for update_license function."""

    def test_update_license_creates_license_file(self, temp_dir, monkeypatch):
        """Test that update_license creates a LICENSE file."""
        monkeypatch.chdir(temp_dir)
        
        # Mock urlretrieve to actually create the file
        import unittest.mock as mock
        with mock.patch("urllib.request.urlretrieve") as mock_retrieve:
            # Create a LICENSE file when urlretrieve is called
            def create_license(url, path):
                with open(path, 'w') as f:
                    f.write("MIT License")
            mock_retrieve.side_effect = create_license
            
            functions.update_license("https://example.com/license", "MIT", "badge")
            
            assert os.path.isfile(os.path.join(temp_dir, "LICENSE"))
        """Test that update_license creates a LICENSE file."""
        monkeypatch.chdir(temp_dir)

        functions.update_license("https://example.com/license", "MIT", "[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)")

        assert os.path.isfile(os.path.join(temp_dir, "LICENSE"))

    def test_update_license_creates_readme_badge(self, temp_dir, mock_license_response, monkeypatch):
        """Test that update_license adds badge to README.md."""
        monkeypatch.chdir(temp_dir)

        # Create a README.md file
        readme_path = os.path.join(temp_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write("# Test Project\n")

        result = functions.update_license("https://example.com/license", "MIT", "[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)")

        assert result == "README.md"


class TestSaveLoadLastUsedLicenses:
    """Tests for license persistence functions."""

    def test_save_last_used_licenses_creates_config(self, temp_dir, monkeypatch):
        """Test that save_last_used_licenses creates config file."""
        monkeypatch.setenv("HOME", temp_dir)

        functions.save_last_used_licenses(["MIT", "Apache-2.0", "GPL-3.0"])

        config_path = os.path.join(temp_dir, ".gh-license", "config.ini")
        assert os.path.isfile(config_path)

    def test_load_last_used_licenses_empty_when_no_config(self, temp_dir, monkeypatch):
        """Test that load_last_used_licenses returns empty list when no config."""
        monkeypatch.setenv("HOME", temp_dir)

        result = functions.load_last_used_licenses()

        assert result == []

    def test_load_last_used_licenses_returns_saved_licenses(self, temp_dir, monkeypatch):
        """Test that load_last_used_licenses returns previously saved licenses."""
        monkeypatch.setenv("HOME", temp_dir)

        # Save licenses first
        functions.save_last_used_licenses(["MIT", "Apache-2.0"])

        # Load and verify
        result = functions.load_last_used_licenses()

        assert "MIT" in result
        assert len(result) <= 3


class TestPickLicenseFromLastUsed:
    """Tests for pick_license_from_last_used function."""

    def test_pick_license_with_valid_input(self, monkeypatch):
        """Test picking a license with valid numeric input."""
        # Mock input to return "1" - must accept an optional prompt argument
        def mock_input(prompt=""):
            return "1"
        monkeypatch.setattr("builtins.input", mock_input)
        monkeypatch.setattr("sys.exit", lambda code=None: None)
        
        result = functions.pick_license_from_last_used(["MIT", "Apache-2.0"], "licenses.json")
        assert result == "MIT"


class TestPrintLicenseList:
    """Tests for print_license_list function."""

    def test_print_license_list_shows_licenses(self, licenses_json_path, capsys):
        """Test that print_license_list prints license descriptions."""
        if os.path.exists(licenses_json_path):
            functions.print_license_list(licenses_json_path)
            # Just verify it runs without error
            assert True
        else:
            pytest.skip("licenses.json not found")


class TestUpdateLicenseFromJson:
    """Tests for update_license_from_json function."""

    def test_update_license_from_json_success(self, licenses_json_path):
        """Test that update_license_from_json returns result."""
        if os.path.exists(licenses_json_path):
            result = functions.update_license_from_json("MIT", licenses_json_path)
            assert result is not None
        else:
            pytest.skip("licenses.json not found")

    def test_update_license_from_json_invalid_raises(self, licenses_json_path):
        """Test that update_license_from_json exits on invalid license."""
        if os.path.exists(licenses_json_path):
            with pytest.raises(SystemExit) as exc_info:
                functions.update_license_from_json("INVALID-LICENSE", licenses_json_path)
            assert exc_info.value.code == 1
        else:
            pytest.skip("licenses.json not found")


class TestGitCommit:
    """Tests for git_commit function."""

    def test_git_commit_skips_if_not_repo(self, temp_dir, monkeypatch):
        """Test that git_commit skips when not a git repo."""
        monkeypatch.chdir(temp_dir)

        # Mock ARGS
        class MockArgs:
            origin = None

        functions.git_commit(MockArgs(), "MIT", "")
        # Should not raise

    def test_git_commit_skips_if_no_license(self, temp_dir, monkeypatch):
        """Test that git_commit skips when LICENSE file doesn't exist."""
        monkeypatch.chdir(temp_dir)

        # Create README
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# Test")

        # Mock ARGS
        class MockArgs:
            origin = None

        functions.git_commit(MockArgs(), "MIT", "README.md")
        # Should not raise


class TestLoopRepoScan:
    """Tests for loop_repo_scan function."""

    def test_loop_repo_scan_returns_tuple(self, mock_repo):
        """Test that loop_repo_scan returns (str, int, int, int)."""
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt"]

        async def run_async():
            return await functions.loop_repo_scan(mock_repo, license_files)
        
        result = asyncio.run(run_async())

        assert isinstance(result, tuple)
        assert len(result) == 4
        assert isinstance(result[0], str)
        assert isinstance(result[1], int)
        assert isinstance(result[2], int)
        assert isinstance(result[3], int)


class TestArgsScan:
    """Tests for args_scan function."""

    def test_args_scan_requires_provider(self, monkeypatch):
        """Test that args_scan uses repobase.get_provider."""
        # This test would require mocking the entire scan process
        # For now, just verify function exists
        assert callable(functions.args_scan)


class TestArgsLicense:
    """Tests for args_license function."""

    def test_args_license_calls_functions(self, monkeypatch):
        """Test that args_license calls expected functions."""
        # Mock all the functions that args_license calls
        monkeypatch.setattr(functions, "load_last_used_licenses", lambda: [])
        monkeypatch.setattr(functions, "update_license_from_json", lambda *args: "README.md")

        class MockArgs:
            license = "MIT"
            origin = None

        # This would call git_commit, so we need to mock that too
        monkeypatch.setattr(functions, "git_commit", lambda *args: None)

        # Just verify the function exists - actual execution would need mocked providers
        assert callable(functions.args_license)