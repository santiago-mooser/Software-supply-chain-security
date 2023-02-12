#!/usr/bin/python

import json
import subprocess
import os



def snyk_open_source(repo_path):
    """Get the open source vulnerabilities for a repository."""
    # Run the snyk test command with a json output and return the results
    # as a dictionary
    results={}
    results =  subprocess.run(
        ['snyk', 'test', repo_path, '--json'], capture_output=True, text=True
    )
    if results.stderr != '':
        print(results.stderr)
        return {}
    else:
        try:
            snyk_output = json.loads(results.stdout)
        except:
            snyk_output = results.stdout
            print(results.stdout)
    return snyk_output



def snyk_container(container_url):
    """Get the open source vulnerabilities for a container."""
    # Run the snyk test command with a json output and return the results
    # as a dictionary
    results={}
    results =  subprocess.run(
        ['snyk', 'container', 'test', container_url, '--json'], capture_output=True, text=True
    )
    if results.stderr != '':
        print(results.stderr)
        return {}
    else:
        return results.stdout




def snyk_code_sast(repo_path):
    """Get the open source vulnerabilities for a repository."""
    # Run the snyk test command with a json output and return the results
    # as a dictionary

    # test whether the repo_path is a valid path
    if not os.path.isdir(repo_path):
        Exception("The path to the repository is not valid")

    results={}
    results =  subprocess.run(
        ['snyk', 'code', 'test', repo_path, '--json'], capture_output=True, text=True
    )
    if results.stderr != '':
        print(results.stderr)
        return {}
    else:
        return results.stdout


def get_git_commit_count(repo_path):
    # Get the number of commits
    if not os.path.isdir(repo_path):
        Exception("The path to the repository is not valid")

    os.chdir(repo_path)
    total_commits = subprocess.check_output("git log --oneline | wc -l", shell=True)
    total_commits = total_commits.decode('utf-8').strip()

    return total_commits


def get_git_signed_commit_count(repo_path):
    # Get the number of signed commits
    if not os.path.isdir(repo_path):
        Exception("The path to the repository is not valid")

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
        print(results.stderr)
        return {}
    else:
        dependabot_output = json.loads(results.stdout)
    return dependabot_output


def run_analysis(repo_path):
    '''Run all the analysis tools on a repository'''
    # Run all the analysis tools on a repository and return the results as a dictionary
    results = {}
    # Get git commit count
    results['git_commit_count'] = get_git_commit_count(repo_path)
    # Get git signed commit count
    results['git_signed_commit_count'] = get_git_signed_commit_count(repo_path)

    # if SNYK_API_KEY and SNYK_ORG_ID are not set, then skip snyk tests
    if os.getenv('SNYK_TOKEN') and os.getenv('SNYK_CFG_ORG'):
        # Get snyk open source vulnerabilities
        results['snyk_open_source'] = snyk_open_source(repo_path)
        # Get snyk code sast vulnerabilities
        results['snyk_code_sast'] = snyk_code_sast(repo_path)
    return results