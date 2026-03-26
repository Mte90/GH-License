"""Tests for ghlicense.cmd module."""
import pytest
import os
import sys

from ghlicense import cmd


class TestArgumentParser:
    """Tests for argument parser configuration."""

    def test_parser_has_scan_option(self):
        """Test that parser has --scan option."""
        args = cmd.PARSER.parse_args(["--scan", "testuser"])
        assert args.scan == "testuser"

    def test_parser_has_license_option(self):
        """Test that parser has --license option."""
        args = cmd.PARSER.parse_args(["--license", "MIT"])
        assert args.license == "MIT"

    def test_parser_has_licenselist_option(self):
        """Test that parser has --licenselist option."""
        args = cmd.PARSER.parse_args(["--licenselist"])
        assert args.licenselist is True

    def test_parser_has_provider_option(self):
        """Test that parser has --provider option."""
        args = cmd.PARSER.parse_args(["--provider", "github"])
        assert args.provider == "github"

    def test_parser_has_report_option(self):
        """Test that parser has --report option."""
        args = cmd.PARSER.parse_args(["--report", "my-report"])
        assert args.report == "my-report"

    def test_parser_has_origin_option(self):
        """Test that parser has --origin option."""
        args = cmd.PARSER.parse_args(["--origin", "upstream"])
        assert args.origin == "upstream"


class TestProviderLoading:
    """Tests for provider loading at module import."""

    def test_parser_description_exists(self):
        """Test that parser has a description."""
        assert cmd.PARSER.description is not None
        assert len(cmd.PARSER.description) > 0


class TestMain:
    """Tests for main function."""

    def test_main_requires_arguments(self, monkeypatch):
        """Test that main requires arguments."""
        monkeypatch.setattr("sys.argv", ["gh-license"])
        
        with pytest.raises(SystemExit) as exc_info:
            cmd.main()
        
        # Should exit with 0 when no args (shows help)
        assert exc_info.value.code == 0


class TestLicensePath:
    """Tests for licenses_path configuration."""

    def test_licenses_path_exists(self):
        """Test that licenses_path points to existing file."""
        licenses_path = cmd.licenses_path
        assert os.path.isfile(licenses_path)

    def test_licenses_path_in_ghlicense_dir(self):
        """Test that licenses_path is in ghlicense directory."""
        licenses_path = cmd.licenses_path
        assert "ghlicense" in str(licenses_path)
        assert "licenses.json" in str(licenses_path)


class TestBackwardCompatibility:
    """Tests for backward compatibility."""

    def test_args_global_exists(self):
        """Test that ARGS global is defined."""
        assert hasattr(cmd, 'ARGS')

    def test_main_function_exists(self):
        """Test main function exists."""
        assert callable(cmd.main)