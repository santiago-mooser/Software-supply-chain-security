#!/bin/python
import json
import logging
import time
import os
import subprocess

import requests

logger = logging.getLogger()
warning = logger.warning
info = logger.info
debug = logger.debug
error = logger.error

"""
Changelog:
1.0.0: First working copy
1.1.0: Added logging and retries to the API calls
"""


version = "1.1.0"

# Get data for most downloaded packages:
def query_api(entries):
    """This function queries the pypi API and returns the first x pages of results"""

    info("Querying pypi API")

    results = {}

    url = (
        "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
    )

    while True:
        response = requests.get(url)

        if response.status_code != 200:
            error("Error getting file")
            time.sleep(5)
            continue
        else:
            break

    debug(f"Data: {json.dumps(response.json(), indent=4)}")

    retrieved_entries = response.json()["rows"]

    results.update({"pypi": retrieved_entries[: int(entries)]})

    # Also get data for most starred repos on github
    url = f"https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&per_page={entries}"

    while True:
        response = requests.get(url)

        if response.status_code != 200:
            error("Error getting stats from github")
            time.sleep(5)
            continue
        else:
            break

    results.update({"github": response.json()})

    info("Successfully retrieved data from Github")
    debug(f"Data: {json.dumps(results, indent=4)}")

    return results


def parse_metadata_to_elasticseach_mapping(api_data):
    """This function takes the data returned my the pypi API and parses it to fit the elasticsearch mapping"""

    info("Parsing data to elasticsearch mapping")

    results = api_data["pypi"]

    parsed_data = {}

    for result in results:

        # We need to do an extra query to the PyPi API to get the repo URL
        url = f"https://pypi.org/pypi/{result['project']}/json"

        while True:
            response = requests.get(url)

            if response.status_code != 200:
                error(
                    f"Error getting repo informaton for {result['project']} from PyPi"
                )
                time.sleep(5)
                continue
            else:
                break

        description = ""
        repo_url = ""

        repo_url = response.json()["info"]["project_urls"].get("Source")
        if repo_url == "" or repo_url is None or "api" in repo_url:
            repo_url = response.json()["info"]["project_urls"].get("Code")
        if repo_url == "" or repo_url is None or "api" in repo_url:
            repo_url = response.json()["info"]["project_urls"].get("Homepage")
        if repo_url == "" or repo_url is None or "api" in repo_url:
            repo_url = response.json()["info"]["package_url"]

        description = response.json()["info"]["summary"]

        parsed_data.update(
            {
                result["project"]: {
                    "source": "pypi",
                    "repo_name": result["project"],
                    "repo_url": repo_url,
                    "description": description,
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

    results = api_data["github"]["items"]

    for result in results:

        parsed_data.update(
            {
                f"{result['name']}": {
                    "source": "github",
                    "repo_name": result["name"],
                    "repo_url": result["clone_url"],
                    "description": result["description"],
                    "snyk_dependency_scan_results": {},
                    "dependabot_results": {},
                    "snyk_sast_results": {},
                    "semgrep_results": {},
                    "git_commit_count": "",
                    "git_commit_signatures_count": "",
                    "git_commit_signatures_percentage": "",
                    "package_signature": "",
                }
            }
        )

    debug(f"Successfully parsed data: {json.dumps(parsed_data, indent=4)}")

    return parsed_data


def install_dependencies(repo_path):
    """Install the dependencies found in the requirements.py file"""
    debug(f"Installing dependencies for {repo_path}")
    # Install the dependencies found in the requirements.py file
    if not os.path.isdir(repo_path):
        error("The path to the repository is not valid")
        return

    os.chdir(repo_path)
    requirements_file = os.path.join(repo_path, "requirements.txt")
    if os.path.isfile(requirements_file):
        debug(f"Installing dependencies from {requirements_file}")
        results = subprocess.run(
            ["pip3", "install", "-r", requirements_file], capture_output=True, text=True
        )
        if results.stderr != '':
            error(f"Error installing dependencies: {results.stderr}")
    else:
        debug(f"No requirements.txt file found in {repo_path}")


def name():
    return "python"
