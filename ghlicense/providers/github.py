from ghlicense import repobase

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
        """Wrapper around github.get_repos()."""
        # Obtain a list of github repos of the user
        g_repos = self.user.get_repos()
        repos = []

        # Iterate over the list of "github repos" and
        # prepare a list of "repos" with properties of interest initialised.
        for g_repo in g_repos:
            raw_base_url = 'http://github.com/' + g_repo.full_name + '/blob/' + g_repo.default_branch + '%s/'
            repo_url = 'http://github.com/' + g_repo.full_name
            repos.append(repobase.Repo(g_repo.full_name, raw_base_url, repo_url,
                                       g_repo.default_branch, g_repo.fork))
        return repos


# Register this Github repo provider with ghlicense
repobase.register_provider("github", GitHubProvider, PROVIDER_PLUGIN_LOADED)
