"""Gitlab provider"""
import asyncio

from ghlicense import repobase
from ghlicense.utils.retry import async_retry, RateLimitError

# By default, assume that this Github provider can be registered.
PROVIDER_PLUGIN_LOADED = True

try:
    # Attempt to import the gitlab module to interact with Github.com
    import gitlab
except ImportError:
    # If the module failed to import, then this gitlab provider can NOT be registered.
    PROVIDER_PLUGIN_LOADED = False


class GitLabProvider(repobase.Provider):
    """Derived a GitLabProvider from repobase.Provider."""

    def __init__(self, username):
        """Initialise the GithubProvider using the gitlab module.

        A handle to the gitlab user is obtained by calling
        gitlab.get_user(username)

        Keyword arguments:
        username -- The Github username.
        """
        super().__init__(username)
        self.gitlab = gitlab.Gitlab()
        self.user = self.gitlab.users.list(username=username)[0]

    def get_repos(self):
        """Wrapper around gitlab.get_repos() - only source repositories by default."""
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
        """Async wrapper around gitlab.get_repos() - only source repositories by default."""
        @async_retry(max_retries=5, base_delay=1)
        async def _fetch_repos():
            return await asyncio.to_thread(self._fetch_repos_sync)

        repos_data = await _fetch_repos()
        repos = []
        for g_repo in repos_data:
            if hasattr(g_repo, 'forked_project') and g_repo.forked_project:
                continue
            raw_base_url = 'https://gitlab.com/' + g_repo.path_with_namespace + '/blob/' + g_repo.default_branch + '/'
            repo_url = 'https://gitlab.com/' + g_repo.path_with_namespace
            repos.append(repobase.Repo(g_repo.path_with_namespace, raw_base_url, repo_url,
                                       g_repo.default_branch, False))
        return repos

    def _fetch_repos_sync(self):
        """Synchronous fetch of repos."""
        return self.user.projects.list(owned=True, include_subgroups=False)


# Register this Github repo provider with ghlicense
repobase.register_provider("gitlab", GitLabProvider, PROVIDER_PLUGIN_LOADED)
