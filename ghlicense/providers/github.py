from ghlicense import repobase

PROVIDER_PLUGIN_LOADED = True

try:
    from github import Github
except:
    PROVIDER_PLUGIN_LOADED = False

class GitHubProvider(repobase.Provider):
    def __init__(self, username):
        self.g = Github()
        self.user = self.g.get_user(username)
    
    def get_repos(self):
        g_repos = self.user.get_repos()
        repos = []
        for g_repo in g_repos:
            repos.append(repobase.Repo(g_repo.full_name, g_repo.default_branch, g_repo.fork))
        return repos

repobase.register_provider("github", GitHubProvider, PROVIDER_PLUGIN_LOADED)
