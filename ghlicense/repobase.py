import sys
from abc import ABCMeta, abstractmethod

# List of current successfully registered i.e. "active" providers.
# These are sources of repos i.e. public repository hosts.
PROVIDERS = {}


class Repo:
    """Contains details of a repository."""

    def __init__(self, full_name, raw_base_url, repo_url, default_branch="master", fork=False):
        """Repo class constructor

        Keyword arguments:
        full_name -- The name of the repo.
        raw_base_url -- The URL link to the "raw" contents of the repo.
        repo_url -- The URL link to the public repo's homepage.
        default_branch -- The branch to check (default "master").
        fork --  Whether the repo is a fork of another repo (default False).
        """
        self.full_name = full_name
        self.raw_base_url = raw_base_url
        self.repo_url = repo_url
        self.default_branch = default_branch
        self.fork = fork


class Provider(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, username):
        pass

    @abstractmethod
    def get_repos(self):
        pass


def register_provider(name, provider_class, loaded=False):
    """Register i.e. Activate a provider.

    Each provider needs to call this function with loaded = True to register
    itself as a supported repo provider.

    Keyword arguments:
    name -- Name of the provider.
    provider_class -- The name of the provider class.
    loaded -- Whether to register the provider (default False).
    """
    if name not in PROVIDERS:
        if loaded:
            PROVIDERS[name] = provider_class
        else:
            PROVIDERS[name] = None


def get_provider(name):
    """Returns whether a repo provider is registered.

    Keyword arguments:
    name -- Name of the provider to check if registered.
    """
    if name in PROVIDERS:
        if not PROVIDERS[name]:
            print("ERROR: Provider '%s' is disabled due to problems." % name)
            sys.exit(1)
        return PROVIDERS[name]
    else:
        print("ERROR: Provider '%s' does not exist!" % name)
        sys.exit(1)


def get_providers():
    """Returns a pair of dicts of providers.

    Each registered provider is in one of the 2 dicts.

    The "good" dict contains successfully loaded providers.
    The "bad" dict contains providers that failed to load/initialise.
    """
    good = []
    bad = []
    for name in PROVIDERS:
        if PROVIDERS[name]:
            good.append(name)
        else:
            bad.append(name)
    return good, bad
