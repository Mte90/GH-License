"""Tests for ghlicense.cli modules."""
import pytest
import sys
from unittest.mock import patch, AsyncMock
from ghlicense.cli import parser
from ghlicense import repobase

try:
    from ghlicense.providers import bitbucket
    HAS_BITBUCKET = True
except ImportError:
    HAS_BITBUCKET = False


class TestCLIParser:
    """Tests for CLI parser."""

    def test_parser_has_scan_option(self):
        """Test parser has --scan option."""
        args = parser.PARSER.parse_args(["--scan", "testuser"])
        assert args.scan == "testuser"

    def test_parser_license_option(self):
        """Test --license option parsing."""
        args = parser.PARSER.parse_args(["--license", "MIT"])
        assert args.license == "MIT"

    def test_parser_provider_option(self):
        """Test --provider option."""
        args = parser.PARSER.parse_args(["--scan", "user", "--provider", "gitlab"])
        assert args.provider == "gitlab"

    def test_parser_report_option(self):
        """Test --report option."""
        args = parser.PARSER.parse_args(["--scan", "user", "--report", "myreport.txt"])
        assert args.report == "myreport.txt"

    def test_parser_origin_option(self):
        """Test --origin option."""
        args = parser.PARSER.parse_args(["--license", "MIT", "--origin", "upstream"])
        assert args.origin == "upstream"

    def test_parser_show_option(self):
        """Test --show option for filtering."""
        args = parser.PARSER.parse_args(["--scan", "user", "--show", "licensed"])
        assert args.show == "licensed"

    def test_parser_show_all_default(self):
        """Test --show defaults to all."""
        args = parser.PARSER.parse_args(["--scan", "user"])
        assert args.show == "all"


class TestCLIParserHelp:
    """Tests for CLI help messages."""

    def test_parser_has_description(self):
        """Test parser has description."""
        parser_obj = parser.PARSER
        assert parser_obj.description is not None

    def test_parser_help_shows_options(self):
        """Test parser help shows options."""
        help_text = parser.PARSER.format_help()
        assert "--scan" in help_text or "--license" in help_text


class TestCLIFunctions:
    """Tests for CLI helper functions."""

    def test_get_providers_list(self):
        """Test getting list of providers."""
        good, bad = repobase.get_providers()
        
        assert isinstance(good, list)
        assert isinstance(bad, list)
        
        # Check registered providers
        assert "github" in repobase.PROVIDERS
        assert "gitlab" in repobase.PROVIDERS

    def test_github_provider_enabled(self):
        """Test GitHub provider is enabled."""
        assert repobase.PROVIDERS.get("github") is not None

    def test_gitlab_provider_enabled(self):
        """Test GitLab provider is enabled."""
        assert repobase.PROVIDERS.get("gitlab") is not None

    @pytest.mark.skipif(not HAS_BITBUCKET, reason="bitbucket module not available")
    def test_bitbucket_provider_enabled(self):
        """Test Bitbucket provider is enabled (if library installed)."""
        assert "bitbucket" in repobase.PROVIDERS


class TestCLIMain:
    """Tests for CLI main function."""

    def test_main_requires_arguments(self):
        """Test main shows help when no arguments."""
        from ghlicense.cli import main as cli_main
        
        with patch.object(sys, 'argv', ['gh-license']):
            with pytest.raises(SystemExit) as exc_info:
                cli_main()
            assert exc_info.value.code == 0

    def test_main_with_scan_arg(self):
        """Test main with scan argument."""
        from ghlicense.cli import main as cli_main
        
        with patch.object(sys, 'argv', ['gh-license', '--scan', 'testuser']):
            with patch('ghlicense.cli.args_scan', new_callable=AsyncMock) as mock_scan:
                with pytest.raises(SystemExit):
                    cli_main()

    def test_main_with_licenselist_arg(self):
        """Test main with license list argument."""
        from ghlicense.cli import main as cli_main
        
        with patch.object(sys, 'argv', ['gh-license', '--licenselist']):
            with patch('ghlicense.cli.print_license_list') as mock_list:
                mock_list.return_value = None
                with pytest.raises(SystemExit):
                    cli_main()

    def test_main_with_license_arg(self):
        """Test main with license argument."""
        from ghlicense.cli import main as cli_main
        
        with patch.object(sys, 'argv', ['gh-license', '--license', 'MIT']):
            with patch('ghlicense.cli.args_license') as mock_license:
                mock_license.return_value = None
                with pytest.raises(SystemExit):
                    cli_main()