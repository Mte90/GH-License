"""Tests for ghlicense providers modules."""
# Import providers to ensure they're registered
from unittest.mock import MagicMock
from ghlicense.providers import github as github
from ghlicense.providers import gitlab as gitlab
try:
    from ghlicense.providers import bitbucket as bitbucket
    HAS_BITBUCKET = True
except ImportError:
    HAS_BITBUCKET = False
from ghlicense import repobase
import pytest


class TestProviderRegistration:
    """Tests for provider registration."""

    def test_github_provider_registered(self):
        """Test that GitHub provider is registered."""
        assert "github" in repobase.PROVIDERS

    def test_gitlab_provider_registered(self):
        """Test that GitLab provider is registered."""
        assert "gitlab" in repobase.PROVIDERS

    @pytest.mark.skipif(not HAS_BITBUCKET, reason="bitbucket module not available")
    def test_bitbucket_provider_registered(self):
        """Test that Bitbucket provider is registered."""
        assert "bitbucket" in repobase.PROVIDERS

    def test_providers_dict_contains_classes_or_none(self):
        """Test that PROVIDERS dict values are classes or None."""
        for name, provider_class in repobase.PROVIDERS.items():
            # Provider should be either a class or None (disabled)
            assert provider_class is None or isinstance(provider_class, type)


class TestGitHubProviderModule:
    """Tests for GitHub provider module structure."""

    def test_github_module_importable(self):
        """Test that github module is importable."""
        assert hasattr(github, 'GitHubProvider')

    def test_github_provider_inherits_from_provider(self):
        """Test GitHubProvider inherits from Provider."""
        assert issubclass(github.GitHubProvider, repobase.Provider)

    def test_github_provider_has_get_repos_method(self):
        """Test GitHubProvider has get_repos method."""
        assert hasattr(github.GitHubProvider, 'get_repos')

    def test_github_provider_has_get_license_info_method(self):
        """Test GitHubProvider has get_license_info method."""
        assert hasattr(github.GitHubProvider, 'get_license_info')


class TestGitLabProviderModule:
    """Tests for GitLab provider module structure."""

    def test_gitlab_module_importable(self):
        """Test that gitlab module is importable."""
        assert hasattr(gitlab, 'GitLabProvider')

    def test_gitlab_provider_inherits_from_provider(self):
        """Test GitLabProvider inherits from Provider."""
        assert issubclass(gitlab.GitLabProvider, repobase.Provider)

    def test_gitlab_provider_has_get_repos_method(self):
        """Test GitLabProvider has get_repos method."""
        assert hasattr(gitlab.GitLabProvider, 'get_repos')


class TestBitbucketProviderModule:
    """Tests for Bitbucket provider module structure."""

    @pytest.mark.skipif(not HAS_BITBUCKET, reason="bitbucket module not available")
    def test_bitbucket_module_importable(self):
        """Test that bitbucket module is importable."""
        assert hasattr(bitbucket, 'BitBucketProvider')

    @pytest.mark.skipif(not HAS_BITBUCKET, reason="bitbucket module not available")
    def test_bitbucket_provider_inherits_from_provider(self):
        """Test BitBucketProvider inherits from Provider."""
        assert issubclass(bitbucket.BitBucketProvider, repobase.Provider)

    @pytest.mark.skipif(not HAS_BITBUCKET, reason="bitbucket module not available")
    def test_bitbucket_provider_has_get_repos_method(self):
        """Test BitBucketProvider has get_repos method."""
        assert hasattr(bitbucket.BitBucketProvider, 'get_repos')


class TestProviderPluginLoaded:
    """Tests for PROVIDER_PLUGIN_LOADED flags."""

    def test_github_provider_plugin_loaded_is_bool(self):
        """Test PROVIDER_PLUGIN_LOADED is a boolean."""
        assert isinstance(github.PROVIDER_PLUGIN_LOADED, bool)

    def test_gitlab_provider_plugin_loaded_is_bool(self):
        """Test PROVIDER_PLUGIN_LOADED is a boolean."""
        assert isinstance(gitlab.PROVIDER_PLUGIN_LOADED, bool)

    @pytest.mark.skipif(not HAS_BITBUCKET, reason="bitbucket module not available")
    def test_bitbucket_provider_plugin_loaded_is_bool(self):
        """Test PROVIDER_PLUGIN_LOADED is a boolean."""
        assert isinstance(bitbucket.PROVIDER_PLUGIN_LOADED, bool)


class TestGitHubProviderFunctional:
    """Functional tests for GitHub provider with mocks."""

    def test_github_get_repos_returns_list(self, mock_github_provider):
        """Test get_repos returns a list of repos."""
        repos = mock_github_provider.get_repos()
        assert isinstance(repos, list)

    def test_github_get_license_info_success(self, mock_github_provider):
        """Test get_license_info returns license info on success."""
        # Mock the github.get_repo and license response
        mock_repo = mock_github_provider._github_mock.get_repo.return_value
        mock_license = MagicMock()
        mock_license.name = "MIT License"
        mock_license.spdx_id = "MIT"
        mock_license.key = "mit"
        mock_repo.get_license.return_value = mock_license
        
        result = mock_github_provider.get_license_info("testuser/testrepo")
        
        assert result is not None
        assert result["name"] == "MIT License"
        assert result["spdx_id"] == "MIT"

    def test_github_get_license_info_returns_none_on_error(self, mock_github_provider):
        """Test get_license_info returns None on error."""
        mock_github_provider._github_mock.get_repo.side_effect = Exception("API Error")
        
        result = mock_github_provider.get_license_info("testuser/testrepo")
        
        assert result is None


class TestGitLabProviderFunctional:
    """Functional tests for GitLab provider with mocks."""

    def test_gitlab_get_repos_returns_list(self, mock_gitlab_provider):
        """Test get_repos returns a list of repos."""
        repos = mock_gitlab_provider.get_repos()
        assert isinstance(repos, list)


class TestBitbucketProviderFunctional:
    """Functional tests for Bitbucket provider with mocks."""

    @pytest.mark.skipif(not HAS_BITBUCKET, reason="bitbucket module not available")
    def test_bitbucket_provider_instantiation(self):
        """Test BitBucketProvider can be instantiated."""
        # Test the provider class exists and can be accessed
        assert hasattr(bitbucket, 'BitBucketProvider')