#!/bin/python
import requests
import json
import logging
import os

logger = logging.getLogger()
warning = logger.warning
info = logger.info
debug = logger.debug
error = logger.error

version="2.0.0"

# Get data for most downloaded javascript packages:
def query_api(entries):

    if entries=="":
        entries="10"

    # sort by popularity and return the top 250 packages
    url=f"https://api.npms.io/v2/search?q=not:unstable+popularity-weight:99.0&size={entries}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error getting file")
    else:
        return response.json()


def parse_metadata_to_elasticseach_mapping(api_data):
    '''This function takes the data returned my the npms API and parses it to fit the elasticsearch mapping'''
    results = api_data["results"]

    parsed_data = {}

    for result in results:
        result = result["package"]
        parsed_data.update({
            result["name"]:{
                "repo_name": result["name"],
                "repo_url": result["links"]["repository"],
                "description": result["description"],
                "version": result["version"],
                "snyk_dependency_scan_results": {},
                "dependabot_results": {},
                "snyk_sast_results": {},
                "semgrep_results": {},
                "git_commit_count": '',
                "git_commit_signatures_count": '',
                "git_commit_signatures_percentage": '',
                "package_signature": ''
            }
        })

    return parsed_data


def install_dependencies(repo_path):
    '''Install the javascript dependencies'''
    info("Installing dependencies")
    try:
        os.system(f"cd {repo_path} && npm install")
        info("Dependencies installed")
        return True
    except Exception as e:
        error(f"Error installing dependencies: {e}")
        return False



def name():
    return "javascript"

