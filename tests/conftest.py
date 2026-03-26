"""Pytest fixtures for gh-license test infrastructure."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_file(temp_dir):
    """Create a temporary file in temp directory."""
    filepath = os.path.join(temp_dir, "test_file.txt")
    with open(filepath, "w") as f:
        f.write("test content")
    yield filepath
    if os.path.exists(filepath):
        os.remove(filepath)


@pytest.fixture
def mock_repo():
    """Create a mock Repo object."""
    from ghlicense import repobase

    repo = repobase.Repo(
        full_name="testuser/testrepo",
        raw_base_url="https://github.com/testuser/testrepo/raw/master/",
        repo_url="https://github.com/testuser/testrepo",
        default_branch="main",
        fork=False,
    )
    yield repo


@pytest.fixture
def mock_github_provider():
    """Create a mock GitHub provider with mocked get_repos."""
    from ghlicense.providers import github

    with patch("ghlicense.providers.github.Github") as mock_github_class:
        mock_github = MagicMock()
        mock_github_class.return_value = mock_github

        mock_user = MagicMock()
        mock_github.get_user.return_value = mock_user

        mock_repo = MagicMock()
        mock_repo.full_name = "testuser/testrepo"
        mock_repo.default_branch = "main"
        mock_repo.fork = False
        mock_user.get_repos.return_value = [mock_repo]

        provider = github.GitHubProvider("testuser")
        provider._github_mock = mock_github
        provider._user_mock = mock_user
        yield provider


67#QP|@pytest.fixture
#YW|def mock_bitbucket_provider():
#KH|    """Create a mock Bitbucket provider with mocked get_repos."""
#HQ|    from ghlicense.providers import bitbucket
#PR|
#QR|    if not bitbucket.PROVIDER_PLUGIN_LOADED:
#QR|        pytest.skip("bitbucket library not installed")
#QR|
#QR|    with patch("ghlicense.providers.bitbucket.Bitbucket") as mock_bb_class:
def mock_bitbucket_provider():
    """Create a mock Bitbucket provider with mocked get_repos."""
    from ghlicense.providers import bitbucket

    with patch("ghlicense.providers.bitbucket.Bitbucket") as mock_bb_class:
        mock_bitbucket = MagicMock()
        mock_bb_class.return_value = mock_bitbucket

        mock_response = (
            True,
            [
                {
                    "slug": "testrepo",
                    "is_fork": False,
                }
            ],
        )
        mock_bitbucket.repository.public.return_value = mock_response

        provider = bitbucket.BitBucketProvider("testuser")
        yield provider


@pytest.fixture
def mock_gitlab_provider():
    """Create a mock GitLab provider with mocked get_repos."""
    from ghlicense.providers import gitlab

    with patch("ghlicense.providers.gitlab.gitlab.Gitlab") as mock_gl_class:
        mock_gitlab = MagicMock()
        mock_gl_class.return_value = mock_gitlab

        mock_user = MagicMock()
        mock_gitlab.users.list.return_value = [mock_user]

        mock_project = MagicMock()
        mock_project.path_with_namespace = "testuser/testrepo"
        mock_project.default_branch = "main"
        mock_user.projects.list.return_value = [mock_project]

        provider = gitlab.GitLabProvider("testuser")
        yield provider


@pytest.fixture
def licenses_json_path():
    """Get the path to licenses.json."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level from tests/ to ghlicense/
    project_dir = os.path.dirname(current_dir)
    licenses_path = os.path.join(project_dir, "ghlicense", "licenses.json")
    yield licenses_path


@pytest.fixture
def mock_license_response():
    """Mock urllib.request.urlretrieve for license downloads."""
    with patch("urllib.request.urlretrieve") as mock_urlretrieve:
        mock_urlretrieve.return_value = None
        yield mock_urlretrieve


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for git operations."""
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "main\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run
