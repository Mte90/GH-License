from ghlicense import repobase
import sys

PROVIDER_PLUGIN_LOADED = True

try:
    from bitbucket.bitbucket import Bitbucket
except:
    PROVIDER_PLUGIN_LOADED = False

class BitBucketProvider(repobase.Provider):
    def __init__(self, username):
        self.bb = Bitbucket()
        self.username = username
    
    def get_repos(self):
        self.bb_repos_resp = self.bb.repository.public(self.username)
        if not self.bb_repos_resp[0]:
            print("ERROR: BitBucket username not found!")
            sys.exit(1)
        self.bb_repos = self.bb_repos_resp[1]
        
        repos = []
        for bb_repo in self.bb_repos:
            full_name = self.username + "/" + bb_repo['slug']
            default_branch = "master"
            raw_base_url = 'http://bitbucket.com/' + full_name + '/raw/' + default_branch + '/'
            repo_url = 'http://bitbucket.com/' + full_name
            repos.append(repobase.Repo(full_name, raw_base_url, repo_url, default_branch, bb_repo['is_fork']))
        return repos


repobase.register_provider("bitbucket", BitBucketProvider, PROVIDER_PLUGIN_LOADED)
