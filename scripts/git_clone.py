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

def clone_git_repo(repo_url, path):
    """Clone a git repository to a given path."""

    # If the path already exists, git pull from inside the path instead of cloning
    if os.path.exists(path):
        info(f"Path {path} already exists, pulling from {repo_url} \n")
        repo = Repo(path)
        origin = repo.remotes.origin

        # try to pull from the repo 5 times before giving up
        for i in range(5):
            try:
                origin.pull()
                return True
            except base.GitCommandError as e:
                error(f"Error pulling from {repo_url}: {e}.\tRetrying...")
                continue

        return False

    # If the path does not exist, clone the repo
    else:
        info(f"{repo_url} not found. Cloning into {path} \n")

        # try to clone the repo 5 times before giving up
        for i in range(5):
            try:
                # clone the default branch
                Repo.clone_from(repo_url, path)
                return True
            except base.GitCommandError as e:
                error(f"Error cloning from {repo_url}: {e}.\tRetrying...")
                try:
                    # Get the default branch name
                    repo = git.Repo.init(path)
                    default_branch = repo.config_reader().get_value("init", "defaultBranch")
                    # Delete the repo and try again
                    os.system(f"rm -rf {path}")
                    Repo.clone_from(repo_url, path, branch=default_branch)
                    continue
                except:
                    error(f"Error cloning from {repo_url}: {e}.\tRetrying...")
                    continue

        return False