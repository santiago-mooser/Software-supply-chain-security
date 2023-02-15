#!/usr/bin/python

import logging
import os

import git
from git import Repo, base

logger = logging.getLogger()
warning = logger.warning
info = logger.info
debug = logger.debug
error = logger.error

def clone_git_repo(args):
    """Clone a git repository to a given path."""

    repo_url, path = args

    # If the path already exists, git pull from inside the path instead of cloning
    if os.path.exists(path):
        info(f"Path {path} already exists, pulling from {repo_url} \n")
        repo = Repo(path)
        origin = repo.remotes.origin
        origin.pull()
        return

    # If the path does not exist, clone the repo
    else:
        info(f"{repo_url} not found. Cloning into {path} \n")
        Repo.clone_from(repo_url, path)
        return