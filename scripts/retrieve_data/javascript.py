#!/bin/python
import logging
import os
import subprocess

import requests

logger = logging.getLogger()
warning = logger.warning
info = logger.info
debug = logger.debug
error = logger.error

version = "2.0.0"

# Get data for most downloaded javascript packages:
def query_api(entries):

    if entries == "":
        entries = "10"

    # sort by popularity and return the top 250 packages
    url = f"https://api.npms.io/v2/search?q=not:unstable+popularity-weight:99.0&size={entries}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error getting file")
    else:
        return response.json()


def parse_metadata_to_elasticseach_mapping(api_data):
    """This function takes the data returned my the npms API and parses it to fit the elasticsearch mapping"""
    results = api_data["results"]
    debug(f"Results: {results}")

    parsed_data = {}

    for result in results:
        try:
            result = result["package"]
            parsed_data.update(
                {
                    result["name"]: {
                        "repo_name": result["name"],
                        "repo_url": result["links"]["repository"],
                        "description": result.get("description"),
                        "version": result.get("version"),
                        "snyk_dependency_scan_results": {},
                        "dependabot_results": {},
                        "snyk_sast_results": {},
                        "semgrep_results": {},
                        "git_commit_count": 0,
                        "git_commit_signatures_count": 0,
                        "git_commit_signatures_percentage": 0,
                        "package_signature": False,
                    }
                }
            )
        except KeyError:
            error(f"Error parsing {result['name']} to elasticsearch mapping. Skipping")
            debug(f"Error parsing {result['name']}: {result}")
            continue

    return parsed_data


def install_dependencies(repo_path):
    """Install the javascript dependencies"""
    info(f"Installing dependencies for {repo_path}")

    # Install the dependencies found in the requirements.py file
    if not os.path.isdir(repo_path):
        error("The path to the repository is not valid")
        return False

    os.chdir(repo_path)
    results = subprocess.run(
        ["npm", "install"],capture_output=True, text=True
    )
    if results.stderr != '':
        error(f"Error installing dependencies for {repo_path}: {results.stderr}")
        return False
    return True


def name():
    return "javascript"
