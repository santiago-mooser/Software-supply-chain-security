#!/usr/bin/python

import json
import logging
import os
import subprocess

logger = logging.getLogger()
warning = logger.warning
info = logger.info
debug = logger.debug
error = logger.error


def snyk_open_source(repo_path):
    """Get the open source vulnerabilities for a repository."""
    debug(f"Running snyk test on {repo_path}")
    # Run the snyk test command with a json output and return the results
    # as a dictionary
    results={}
    results =  subprocess.run(
        ['snyk', 'test', repo_path, '--json'], capture_output=True, text=True
    )
    if results.stderr != '':
        error(results.stderr)
    try:
        snyk_output = json.loads(results.stdout)
    except:
        error(results.stdout)
        return {}
    return snyk_output



def snyk_container(container_url):
    """Get the open source vulnerabilities for a container."""
    debug(f"Running snyk container test on {container_url}")

    results =  subprocess.run(
        ['snyk', 'container', 'test', container_url, '--json'], capture_output=True, text=True
    )
    if results.stderr != '':
        error(results.stderr)
    try:
        snyk_output = json.loads(results.stdout)
    except:
        error(results.stdout)
        return {}
    debug(snyk_output)
    return snyk_output




def snyk_code_sast(repo_path):
    """Get the open source vulnerabilities for a repository."""
    debug(f"Running snyk code test on {repo_path}")
    # Run the snyk test command with a json output and return the results
    # as a dictionary

    # test whether the repo_path is a valid path
    if not os.path.isdir(repo_path):
        error("The path to the repository is not valid")
        return

    results={}
    results =  subprocess.run(
        ['snyk', 'code', 'test', repo_path, '--json'], capture_output=True, text=True
    )
    if results.stderr != '':
        error(results.stderr)
    try:
        snyk_output = json.loads(results.stdout)
    except:
        error(results.stdout)
        return {}
    debug(snyk_output)
    return snyk_output


def get_git_commit_count(repo_path):
    debug(f"Getting the number of commits for {repo_path}")
    # Get the number of commits
    if not os.path.isdir(repo_path):
        error("The path to the repository is not valid")
        return ""

    os.chdir(repo_path)
    total_commits = subprocess.check_output("git log --oneline | wc -l", shell=True)
    total_commits = total_commits.decode('utf-8').strip()

    debug(f"Total commits for {repo_path}: {total_commits}")
    return total_commits


def get_git_signed_commit_count(repo_path):
    debug(f"Getting the number of signed commits for {repo_path}")
    # Get the number of signed commits
    if not os.path.isdir(repo_path):
        error("The path to the repository is not valid")
        return ""

    os.chdir(repo_path)

    # Get the number of signed commits
    signed_commits = subprocess.check_output("git log --show-signature | grep 'gpg: Good signature' -B3 | grep 'commit' | awk '{print $2}' | wc -l", shell=True)
    signed_commits = signed_commits.decode('utf-8').strip()

    return signed_commits


def dependabot_open_source(repo_path):
    '''Use dependabot to check for open source vulnerabilities'''
    # Run the dependabot test command with a json output and return the results
    # as a dictionary
    results={}
    results =  subprocess.run(
        ['dependabot', 'security', 'check', '--directory', repo_path, '--format', 'json'], capture_output=True, text=True
    )
    if results.stderr != '':
        error (results.stderr)

    try:
        dependabot_output = json.loads(results.stdout)
    except:
        error(results.stdout)
        return {}
    debug(dependabot_output)
    return dependabot_output


def run_analysis(args):

    repo, path = args
    '''Run all the analysis tools on a repository'''
    # Run all the analysis tools on a repository and return the results as a dictionary
    repo_path = os.path.join(path, repo)

    results = {}

    # Get git commit count
    debug(f"Getting percentage of signed commits for {repo_path}")
    results['git_commit_count'] = get_git_commit_count(repo_path)

    # Get git signed commit count
    debug(f"Getting percentage of signed commits for {repo_path}")
    results['git_commit_signatures_count'] = get_git_signed_commit_count(repo_path)

    debug(f"{repo_path} has {results['git_commit_signatures_count']}/{results['git_commit_count']} signed commits")

    # if SNYK_API_KEY and SNYK_ORG_ID are not set, then skip snyk tests
    if os.getenv('SNYK_TOKEN') and os.getenv('SNYK_CFG_ORG'):

        debug(f"SNYK_TOKEN and SNYK_CFG_ORG are set, running snyk tests")

        # Get snyk open source vulnerabilities
        results['snyk_dependency_scan_results'] = snyk_open_source(repo_path)

        # Get snyk code sast vulnerabilities
        results['snyk_sast_results'] = snyk_code_sast(repo_path)

    info(f"Analysis of {repo} complete")
    return {repo: results}