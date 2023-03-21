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
        error(f"The path to the repository is not valid: {repo_path}")
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
        error(f"The path to the repository is not valid {repo_path}")
        return ""

    os.chdir(repo_path)
    total_commits = subprocess.check_output("git log --oneline | wc -l", shell=True)
    total_commits = total_commits.decode('utf-8').strip()

    if int(total_commits) == 0:
        error(f"Could not get the number of commits for {repo_path}")
        return 0

    debug(f"Total commits for {repo_path}: {total_commits}")
    return int(total_commits)


def get_git_signed_commit_count(repo_path):
    debug(f"Getting the number of signed commits for {repo_path}")
    # Get the number of signed commits
    if not os.path.isdir(repo_path):
        error(f"The path to the repository is not valid {repo_path}")
        return ""

    os.chdir(repo_path)

    # Get the number of signed commits
    signed_commits = subprocess.check_output("git log --show-signature | grep 'gpg: Good signature' -B3 | grep 'commit' | awk '{print $2}' | wc -l", shell=True)
    signed_commits = signed_commits.decode('utf-8').strip()

    return int(signed_commits)


def semgrep (repo_path):
    '''Use semgrep to check for vulnerabilities'''
    debug(f"Running semgrep on {repo_path}")
    # Run the semgrep test command with a json output and return the results
    # as a dictionary
    results={}
    results =  subprocess.run(
        ['semgrep', '--config', 'p/ci', '--json', repo_path], capture_output=True, text=True
    )
    if results.stderr != '':
        error (results.stderr)

    try:
        semgrep_output = json.loads(results.stdout)
    except:
        error(results.stdout)
        return {}
    debug(f"Semgrep output for {repo_path}: {semgrep_output}")
    return semgrep_output


def dependabot_open_source(repo_path):
    '''Use dependabot to check for open source vulnerabilities'''
    debug(f"Running dependabot on {repo_path}")
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
    debug(f"Dependabot output for {repo_path}: {dependabot_output}")
    return dependabot_output



def run_analysis(repo_path, language, parsed_data):
    '''Run all the analysis tools on a repository'''

    # Get git commit count
    debug(f"Getting percentage of signed commits for {repo_path}")
    parsed_data['git_commit_count'] = int(get_git_commit_count(repo_path))

    # Get git signed commit count
    debug(f"Getting percentage of signed commits for {repo_path}")
    parsed_data['git_commit_signatures_count'] = int(get_git_signed_commit_count(repo_path))

    # Get percentage of signed commits
    if int(parsed_data['git_commit_count']) > 0:
        parsed_data['git_commit_signatures_percentage'] = int(parsed_data['git_commit_signatures_count']) / int(parsed_data['git_commit_count']) * 100
    else:
        parsed_data['git_commit_signatures_percentage'] = 0

    debug(f"{repo_path} has {parsed_data['git_commit_signatures_count']}/{parsed_data['git_commit_count']} signed commits")

    # Run semgrep
    parsed_data['semgrep_results'] = semgrep(repo_path)
    debug(f"Semgrep results for {repo_path}: {parsed_data['semgrep_results']}")


    # if SNYK_API_KEY and SNYK_ORG_ID are not set, then skip snyk tests
    if os.getenv('SNYK_TOKEN') and os.getenv('SNYK_CFG_ORG'):

        debug(f"SNYK_TOKEN and SNYK_CFG_ORG are set, running snyk tests")

        # Get snyk code sast vulnerabilities
        parsed_data['snyk_sast_results'] = snyk_code_sast(repo_path)

        if not language.install_dependencies(repo_path):
            info(f"Skipping Snyk analysis of {repo_path} due to missing dependencies")
            return parsed_data

        # Get snyk open source vulnerabilities
        parsed_data['snyk_dependency_scan_results'] = snyk_open_source(repo_path)

    info(f"Analysis of {repo_path} complete")
    debug(f"Analysis results for {repo_path}: {parsed_data}")
    return parsed_data