"""Load providers"""
import sys
import logging
from abc import ABCMeta, abstractmethod

from typing import Dict, List, Tuple, Type
# List of current successfully registered i.e. "active" providers.
# These are sources of repos i.e. public repository hosts.
PROVIDERS: Dict[str, Type["Provider"] | None] = {}


class Repo:
    """Contains details of a repository."""

    def __init__(
        self,
        full_name: str,
        raw_base_url: str,
        repo_url: str,
        default_branch: str = "master",
        fork: bool = False,
    ) -> None:
        """Repo class constructor

        Keyword arguments:
        full_name -- The name of the repo.
        raw_base_url -- The URL link to the "raw" contents of the repo.
        repo_url -- The URL link to the public repo's homepage.
        default_branch -- The branch to check (default "master").
        fork --  Whether the repo is a fork of another repo (default False).
        """
        self.full_name: str = full_name
        self.raw_base_url: str = raw_base_url
        self.repo_url: str = repo_url
        self.default_branch: str = default_branch
        self.fork: bool = fork


class Provider(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, username: str) -> None:
        pass

    @abstractmethod
    def get_repos(self) -> List[Repo]:
        pass

def register_provider(
    name: str,
    provider_class: Type["Provider"] | None,
    loaded: bool = False,
) -> None:
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


def get_provider(name: str) -> Type["Provider"]:
    """Returns whether a repo provider is registered.

    Keyword arguments:
    name -- Name of the provider to check if registered.
    """
    if name in PROVIDERS:
        if not PROVIDERS[name]:
            logging.error(f"Provider '{name}' is disabled due to problems.")
            sys.exit(1)
        return PROVIDERS[name]  # type: ignore[return-value]

    logging.error(f"Provider '{name}' does not exist!")
    sys.exit(1)


def get_providers() -> Tuple[List[str], List[str]]:
    """Returns a pair of dicts of providers.

    Each registered provider is in one of the 2 dicts.

    The "good" dict contains successfully loaded providers.
    The "bad" dict contains providers that failed to load/initialise.
    """
    good: List[str] = []
    bad: List[str] = []
    for provider in PROVIDERS.items():
        if provider[1]:  # Check if provider class is not None
            good.append(provider[0])
        else:
            bad.append(provider[0])
    return good, bad
