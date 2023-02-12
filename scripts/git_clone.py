#!/usr/bin/python

import git
from git import base
from git import Repo
import os


def clone_git_repo(args):
    """Clone a git repository to a given path."""

    repo_url, path = args

    # If the path already exists, git pull from inside the path instead of cloning
    if os.path.exists(path):
        print(f"Path {path} already exists, pulling from {repo_url} \n")
        repo = Repo(path)
        origin = repo.remotes.origin
        origin.pull()
        return

    # If the path does not exist, clone the repo
    else:
        print(f"Cloning {repo_url} into {path} \n")
        Repo.clone_from(repo_url, path)
        return