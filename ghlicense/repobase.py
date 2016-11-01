import sys
from abc import ABCMeta, abstractmethod

global providers
providers = {}

class Repo:
    def __init__(self, full_name, default_branch = "master", fork = False):
        self.full_name = full_name
        self.default_branch = default_branch
        self.fork = fork

class Provider(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, username):
        pass
    
    @abstractmethod
    def get_repos(self):
        pass

def register_provider(name, provider_class, loaded = False):
    if name not in providers:
        if loaded:
            providers[name] = provider_class
        else:
            providers[name] = None

def get_provider(name):
    if name in providers:
        if not providers[name]:
            print("ERROR: Provider '%s' is disabled due to problems." % name)
            sys.exit(1)
        return providers[name]
    else:
        print("ERROR: Provider '%s' does not exist!" % name)
        sys.exit(1)

def get_providers():
    good = []
    bad = []
    for name in providers:
        if providers[name]:
            good.append(name)
        else:
            bad.append(name)
    return good, bad
