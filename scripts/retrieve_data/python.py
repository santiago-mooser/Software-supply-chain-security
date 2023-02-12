#!/bin/python
import requests
import json
import argparse

version="1.0.0"

# Get data for most downloaded packages:
def query_api(entries):

    results = {}

    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error getting file")

    results.update({"pypi": response.json()["rows"][:entries]})

    url = f"https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc&per_page={entries}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error getting file")

    else:
        results.update({"github": response.json()})

    return results



def parse_metadata_to_elasticseach_mapping(api_data):
    '''This function takes the data returned my the pypi API and parses it to fit the elasticsearch mapping'''

    results = api_data["pypi"]

    parsed_data = {}

    for result in results:

        # We need to do an extra query to the PyPi API to get the repo URL
        url = f"https://pypi.org/pypi/{result['project']}/json"

        response = requests.get(url)

        description = ""
        repo_url = ""

        if response.status_code != 200:
            print("Error getting file")
            Exception("Error getting file")
        else:
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

    return parsed_data
