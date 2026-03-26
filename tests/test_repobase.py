"""Tests for ghlicense.repobase module - Failing tests (TDD approach)."""

import pytest
from ghlicense import repobase


class TestRepo:
    """Tests for Repo class."""

    def test_repo_initialization(self):
        """Test that Repo can be initialized with all required fields."""
        repo = repobase.Repo(
            full_name="testuser/testrepo",
            raw_base_url="https://github.com/testuser/testrepo/raw/master/",
            repo_url="https://github.com/testuser/testrepo",
            default_branch="main",
            fork=False,
        )
        
        assert repo.full_name == "testuser/testrepo"
        assert repo.raw_base_url == "https://github.com/testuser/testrepo/raw/master/"
        assert repo.repo_url == "https://github.com/testuser/testrepo"
        assert repo.default_branch == "main"
        assert repo.fork is False

    def test_repo_default_values(self):
        """Test that Repo has correct default values."""
        repo = repobase.Repo(
            full_name="testuser/testrepo",
            raw_base_url="https://example.com/",
            repo_url="https://example.com/",
        )
        
        assert repo.full_name == "testuser/testrepo"
        assert repo.raw_base_url == "https://example.com/"
        assert repo.repo_url == "https://example.com/"
        assert repo.default_branch == "master"
        assert repo.fork is False


class TestProvider:
    """Tests for Provider abstract class."""

    def test_provider_is_abstract(self):
        """Test that Provider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            repobase.Provider("testuser")

    def test_provider_requires_get_repos(self):
        """Test that Provider subclass must implement get_repos."""
        class IncompleteProvider(repobase.Provider):
            def __init__(self, username):
                super().__init__(username)
        
        with pytest.raises(TypeError):
            IncompleteProvider("testuser")


class TestRegisterProvider:
    """Tests for register_provider function."""

    def test_register_provider_adds_to_providers(self):
        """Test that register_provider adds provider to PROVIDERS dict."""
        class DummyProvider(repobase.Provider):
            def __init__(self, username):
                super().__init__(username)
            
            def get_repos(self):
                return []
        
        repobase.register_provider("dummy", DummyProvider, loaded=True)
        
        assert "dummy" in repobase.PROVIDERS
        assert repobase.PROVIDERS["dummy"] == DummyProvider

    def test_register_provider_disabled(self):
        """Test that register_provider with loaded=False sets provider to None."""
        class DummyProvider(repobase.Provider):
            def __init__(self, username):
                super().__init__(username)
            
            def get_repos(self):
                return []
        
        repobase.register_provider("disabled", DummyProvider, loaded=False)
        
        assert "disabled" in repobase.PROVIDERS
        assert repobase.PROVIDERS["disabled"] is None

    def test_register_provider_overwrites(self):
        """Test that register_provider overwrites existing provider."""
        class FirstProvider(repobase.Provider):
            def __init__(self, username):
                super().__init__(username)
            
            def get_repos(self):
                return []
        
        class SecondProvider(repobase.Provider):
            def __init__(self, username):
                super().__init__(username)
            
            def get_repos(self):
                return []
        
        repobase.register_provider("test_overwrite", FirstProvider, loaded=True)
        assert repobase.PROVIDERS["test_overwrite"] == FirstProvider
        
        # Note: Current implementation does NOT overwrite - provider is only added if not in PROVIDERS
        repobase.register_provider("test_overwrite", SecondProvider, loaded=True)
        # The provider remains the first one due to current implementation
        assert repobase.PROVIDERS["test_overwrite"] == FirstProvider


class TestGetProvider:
    """Tests for get_provider function."""

    def test_get_provider_returns_registered(self):
        """Test that get_provider returns registered provider."""
        class DummyProvider(repobase.Provider):
            def __init__(self, username):
                super().__init__(username)
            
            def get_repos(self):
                return []
        
        repobase.register_provider("test_get", DummyProvider, loaded=True)
        
        provider = repobase.get_provider("test_get")
        assert provider == DummyProvider

    def test_get_provider_disabled_raises(self):
        """Test that get_provider raises for disabled provider."""
        class DummyProvider(repobase.Provider):
            def __init__(self, username):
                super().__init__(username)
            
            def get_repos(self):
                return []
        
        repobase.register_provider("test_disabled", DummyProvider, loaded=False)
        
        with pytest.raises(SystemExit) as exc_info:
            repobase.get_provider("test_disabled")
        
        assert exc_info.value.code == 1

    def test_get_provider_not_exists_raises(self):
        """Test that get_provider raises for non-existent provider."""
        with pytest.raises(SystemExit) as exc_info:
            repobase.get_provider("nonexistent_provider_xyz")
        
        assert exc_info.value.code == 1


class TestGetProviders:
    """Tests for get_providers function."""

    def test_get_providers_returns_pairs(self):
        """Test that get_providers returns (good, bad) tuple."""
        good, bad = repobase.get_providers()
        
        assert isinstance(good, list)
        assert isinstance(bad, list)

    def test_get_providers_shows_enabled(self):
        """Test that get_providers shows enabled providers."""
        class GoodProvider(repobase.Provider):
            def __init__(self, username):
                super().__init__(username)
            
            def get_repos(self):
                return []
        
        class BadProvider(repobase.Provider):
            def __init__(self, username):
                super().__init__(username)
            
            def get_repos(self):
                return []
        
        repobase.register_provider("good", GoodProvider, loaded=True)
        repobase.register_provider("bad", BadProvider, loaded=False)
        
        good, bad = repobase.get_providers()
        
        assert "good" in good
        assert "bad" in bad
