import sys

from ghlicense import repobase

# By default, assume that this bitbucket provider can be registered.
PROVIDER_PLUGIN_LOADED = True

try:
    # Attempt to import the BitBucket module to interact with Bitbucket.org
    from bitbucket.bitbucket import Bitbucket
except ImportError:
    # If the module failed to import, then this bitbucket provider can NOT be registered.
    PROVIDER_PLUGIN_LOADED = False


class BitBucketProvider(repobase.Provider):
    """Derived a BitBucketProvider from repobase.Provider."""

    def __init__(self, username):
        """Initialise the BitBucketProvider using the Bitbucket module.

        The Bitbucket username is initialised to username.

        Keyword arguments:
        username -- The Bitbucket username.
        """
        super().__init__(username)
        self.bitbucket = Bitbucket()
        self.username = username

    def get_repos(self):
        """Wrapper around BitBucket.repository.public()."""
        # Attempt to obtain the list of public BitBucket repos of the user
        bb_repos_resp = self.bitbucket.repository.public(self.username)

        # If result is empty then quit
        if not bb_repos_resp[0]:
            print("ERROR: BitBucket username not found!")
            sys.exit(1)
        # else we now have a list of BitBucket repos of the user.
        bb_repos = bb_repos_resp[1]
        repos = []

        # Iterate over the list of "BitBucket repos" and
        # prepare a list of "repos" with properties of interest initialised.
        for bb_repo in bb_repos:
            full_name = self.username + "/" + bb_repo['slug']
            default_branch = "master"
            raw_base_url = 'http://bitbucket.com/' + \
                full_name + '/raw/' + default_branch + '/'
            repo_url = 'http://bitbucket.com/' + full_name
            repos.append(repobase.Repo(full_name, raw_base_url, repo_url,
                                       default_branch, bb_repo['is_fork']))
        return repos


# Register this Bitbucket repo provider with ghlicense
repobase.register_provider(
    "bitbucket", BitBucketProvider, PROVIDER_PLUGIN_LOADED)
