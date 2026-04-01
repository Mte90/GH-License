"""Github provider"""
import asyncio
import logging

from ghlicense import repobase
from ghlicense.utils.retry import async_retry, RateLimitError

# By default, assume that this Github provider can be registered.
PROVIDER_PLUGIN_LOADED = True

try:
    # Attempt to import the github module to interact with Github.com
    from github import Github
except ImportError:
    # If the module failed to import, then this github provider can NOT be registered.
    PROVIDER_PLUGIN_LOADED = False


class GitHubProvider(repobase.Provider):
    """Derived a GithubProvider from repobase.Provider."""

    def __init__(self, username):
        """Initialise the GithubProvider using the github module.

        A handle to the github user is obtained by calling
        github.get_user(username)

        Keyword arguments:
        username -- The Github username.
        """
        super().__init__(username)
        self.github = Github()
        self.user = self.github.get_user(username)

    def get_repos(self):
        """Wrapper around github.get_repos() - only source repositories by default."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running event loop - create a new one
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self.get_repos_async())
            finally:
                loop.close()
        else:
            # There's a running loop - use it
            return loop.run_until_complete(self.get_repos_async())

    async def get_repos_async(self):
        """Async wrapper around github.get_repos() - only source repositories by default."""
        @async_retry(max_retries=5, base_delay=1)
        async def _fetch_repos():
            return await asyncio.to_thread(self._fetch_repos_sync)

        repos_data = await _fetch_repos()
        repos = []
        for g_repo in repos_data:
            raw_base_url = 'https://github.com/' + g_repo.full_name + '/blob/' + g_repo.default_branch + '/'
            repo_url = 'https://github.com/' + g_repo.full_name
            repos.append(repobase.Repo(g_repo.full_name, raw_base_url, repo_url,
                                       g_repo.default_branch, g_repo.fork))
        return repos

    def _fetch_repos_sync(self):
        """Synchronous fetch of repos."""
        return list(self.user.get_repos(type="source"))

    def get_license_info(self, repo_name):
        try:
            repo = self.github.get_repo(repo_name)
            license_info = repo.get_license()
            if license_info:
                return {
                    "name": license_info.name,
                    "spdx_id": license_info.spdx_id,
                    "key": license_info.key,
                }
        except Exception as e:
            logging.debug(f"Failed to get license info for {repo_name}: {e}")
        return None


# Register this Github repo provider with ghlicense
repobase.register_provider("github", GitHubProvider, PROVIDER_PLUGIN_LOADED)
