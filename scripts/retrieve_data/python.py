#!/bin/python
import json
import logging
import time

import requests

logger = logging.getLogger()
warning = logger.warning
info = logger.info
debug = logger.debug
error = logger.error

'''
Changelog:
1.0.0: First working copy
1.1.0: Added logging and retries to the API calls
'''


version="1.1.0"

# Get data for most downloaded packages:
def query_api(entries):

    results = {}

    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"

    while True:
        response = requests.get(url)

        if response.status_code != 200:
            error("Error getting file")
            time.sleep(5)
            continue
        else:
            break

    info("Successfully retrieved data from PyPi")
    results.update({"pypi": response.json()["rows"][:entries]})

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

    debug(f"Successfully retrieved data from github: {json.dumps(results, indent=4)}")

    return results



def parse_metadata_to_elasticseach_mapping(api_data):
    '''This function takes the data returned my the pypi API and parses it to fit the elasticsearch mapping'''

    results = api_data["pypi"]

    parsed_data = {}

    for result in results:

        # We need to do an extra query to the PyPi API to get the repo URL
        url = f"https://pypi.org/pypi/{result['project']}/json"

        while True:
            response = requests.get(url)

            if response.status_code != 200:
                error(f"Error getting repo informaton for {result['project']} from PyPi")
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

        parsed_data.update({
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
                "package_signature": False
            }
        })

    results = api_data["github"]["items"]

    for result in results:

        parsed_data.update({
            f"{result['name']}": {
                "source": "github",
                "repo_name": result["name"],
                "repo_url": result["clone_url"],
                "description": result["description"],
                "snyk_dependency_scan_results": {},
                "dependabot_results": {},
                "snyk_sast_results": {},
                "semgrep_results": {},
                "git_commit_count": 0,
                "git_commit_signatures_count": 0,
                "git_commit_signatures_percentage": 0,
                "package_signature": False
            }
        })

    debug(f"Successfully parsed data: {json.dumps(parsed_data, indent=4)}")
    return parsed_data
