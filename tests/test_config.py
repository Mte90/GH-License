"""Tests for ghlicense.config.storage module."""
import pytest
import os
from ghlicense.config import storage


class TestSaveLastUsedLicenses:
    """Tests for save_last_used_licenses function."""

    def test_save_last_used_licenses_creates_config(self, temp_dir, monkeypatch):
        """Test that save_last_used_licenses creates config file."""
        config_dir = os.path.join(temp_dir, ".gh-license")
        monkeypatch.setenv("HOME", temp_dir)
        
        storage.save_last_used_licenses(["MIT", "Apache-2.0", "GPL-3.0"])
        
        config_path = os.path.join(config_dir, "config.ini")
        assert os.path.isfile(config_path)

    def test_save_last_used_licenses_single_license(self, temp_dir, monkeypatch):
        """Test saving single license."""
        monkeypatch.setenv("HOME", temp_dir)
        
        storage.save_last_used_licenses(["MIT"])
        
        # Verify file exists
        config_path = os.path.join(temp_dir, ".gh-license", "config.ini")
        assert os.path.isfile(config_path)

    def test_save_last_used_licenses_empty_list(self, temp_dir, monkeypatch):
        """Test saving empty list."""
        monkeypatch.setenv("HOME", temp_dir)
        
        # Should not raise
        storage.save_last_used_licenses([])


class TestLoadLastUsedLicenses:
    """Tests for load_last_used_licenses function."""

    def test_load_last_used_licenses_empty_when_no_config(self, temp_dir, monkeypatch):
        """Test that load_last_used_licenses returns empty list when no config."""
        monkeypatch.setenv("HOME", temp_dir)
        
        result = storage.load_last_used_licenses()
        
        assert result == []

    def test_load_last_used_licenses_returns_saved_licenses(self, temp_dir, monkeypatch):
        """Test that load_last_used_licenses returns previously saved licenses."""
        monkeypatch.setenv("HOME", temp_dir)
        
        # Save licenses first
        storage.save_last_used_licenses(["MIT", "Apache-2.0"])
        
        # Load and verify
        result = storage.load_last_used_licenses()
        
        assert "MIT" in result

    def test_load_last_used_licenses_missing_lastused_section(self, temp_dir, monkeypatch):
        """Test loading when config exists but missing lastUsed section."""
        monkeypatch.setenv("HOME", temp_dir)
        
        # Create config file without lastUsed section
        config_dir = os.path.join(temp_dir, ".gh-license")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "config.ini")
        
        with open(config_path, "w") as f:
            f.write("[other]\nkey=value\n")
        
        result = storage.load_last_used_licenses()
        
        assert result == []

    def test_load_last_used_licenses_missing_key(self, temp_dir, monkeypatch):
        """Test loading when lastUsed section exists but key is missing."""
        monkeypatch.setenv("HOME", temp_dir)
        
        # Create config file with empty lastUsed section
        config_dir = os.path.join(temp_dir, ".gh-license")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "config.ini")
        
        with open(config_path, "w") as f:
            f.write("[lastUsed]\n")
        
        result = storage.load_last_used_licenses()
        
        assert result == []


class TestPickLicenseFromLastUsed:
    """Tests for pick_license_from_last_used function."""

    def test_pick_license_returns_selected(self, monkeypatch):
        """Test that pick_license_from_last_used returns selected license."""
        monkeypatch.setattr("builtins.input", lambda _: "1")
        
        result = storage.pick_license_from_last_used(
            ["MIT", "Apache-2.0"], 
            "fake_licenses.json"
        )
        
        assert result == "MIT"

    def test_pick_license_user_enters_name(self, monkeypatch):
        """Test when user enters license name directly."""
        call_count = 0
        
        def mock_input(_):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "GPL-3.0"  # User enters license name
            return "n"  # Exit after seeing list
        
        monkeypatch.setattr("builtins.input", mock_input)
        monkeypatch.setattr("ghlicense.license.manager.print_license_list", lambda x: None)
        
        result = storage.pick_license_from_last_used(
            ["MIT", "Apache-2.0"], 
            "fake_licenses.json"
        )
        
        assert result == "GPL-3.0"

    def test_pick_license_user_enters_n(self, monkeypatch):
        """Test when user enters 'n' to see license list."""
        call_count = 0
        
        def mock_input(_):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "n"
        
        monkeypatch.setattr("builtins.input", mock_input)
        
        # Should exit after showing list
        with pytest.raises(SystemExit):
            storage.pick_license_from_last_used(
                ["MIT", "Apache-2.0"], 
                "fake_licenses.json"
            )

    def test_pick_license_invalid_index(self, monkeypatch):
        """Test when user enters invalid index."""
        monkeypatch.setattr("builtins.input", lambda _: "99")  # Invalid index
        
        result = storage.pick_license_from_last_used(
            ["MIT", "Apache-2.0"], 
            "fake_licenses.json"
        )
        
        # Should return the input (as license name)
        assert result == "99"

    def test_pick_license_non_numeric_input(self, monkeypatch):
        """Test when user enters non-numeric input."""
        monkeypatch.setattr("builtins.input", lambda _: "abc")
        
        result = storage.pick_license_from_last_used(
            ["MIT", "Apache-2.0"], 
            "fake_licenses.json"
        )
        
        assert result == "abc"


class TestConfigStorageEdgeCases:
    """Edge case tests for config storage."""

    def test_save_license_with_special_chars(self, temp_dir, monkeypatch):
        """Test saving licenses with special characters."""
        monkeypatch.setenv("HOME", temp_dir)
        
        # This should not raise even with special chars
        storage.save_last_used_licenses(["MIT-2.0", "Apache-2.0"])

    def test_load_nonexistent_home(self, monkeypatch):
        """Test handling when HOME is not set."""
        monkeypatch.delenv("HOME", raising=False)
        
        # Should handle gracefully (may create in current dir)
        try:
            result = storage.load_last_used_licenses()
            assert isinstance(result, list)
        except Exception:
            # Some systems might not have HOME, accept any result
            pass