"""Gitlab provider"""
from ghlicense import repobase

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
        """Wrapper around gitlab.get_repos()."""
        # Obtain a list of gitlab repos of the user
        g_repos = self.user.projects.list()
        repos = []

        # Iterate over the list of "gitlab repos" and
        # prepare a list of "repos" with properties of interest initialised.
        for g_repo in g_repos:
            raw_base_url = 'http://gitlab.com/' + g_repo.path_with_namespace + '/blob/' + g_repo.default_branch + '/'
            repo_url = 'http://gitlab.com/' + g_repo.path_with_namespace
            repos.append(repobase.Repo(g_repo.path_with_namespace, raw_base_url, repo_url,
                                       g_repo.default_branch, False))
        return repos


# Register this Github repo provider with ghlicense
repobase.register_provider("gitlab", GitLabProvider, PROVIDER_PLUGIN_LOADED)
