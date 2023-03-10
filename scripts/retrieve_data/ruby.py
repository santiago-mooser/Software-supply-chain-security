#!/bin/python
import requests
import json
import logging
import os

version="1.0.0"


logger = logging.getLogger()
warning = logger.warning
info = logger.info
debug = logger.debug
error = logger.error


def query_api(entries):
    '''This function queries the rubygems API and returns the first 10 pages of results'''
    info("Querying rubygems API")

    # Get results from first 10 pages of ruby API:
    packages_information = []

    for page in range(0, int(entries)//10):
        url = f"https://rubygems.org/api/v1/search.json?query=*&page={page}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error querying rubygems API for page {page}")
        else:
            packages_information += response.json()

    debug(f"Data: {json.dumps(packages_information, indent=4)}")
    return packages_information


def parse_metadata_to_elasticseach_mapping(api_data):
    '''This function takes the data returned my the rubygems API and parses it to fit the elasticsearch mapping'''
    info("Parsing data to elasticsearch mapping")

    results = api_data

    parsed_data = {}

    for result in results:

        parsed_data.update({
            result["name"]: {
                "repo_name": result["name"],
                "repo_url": result["source_code_uri"],
                "description": result["info"],
                "version": result["version"],
                "snyk_dependency_scan_results": {},
                "dependabot_results": {},
                "snyk_sast_results": {},
                "semgrep_results": {},
                "git_commit_count": '',
                "git_commit_signatures_count": '',
                "git_commit_signatures_percentage": '',
                "package_signature": '',
            }
        })

    debug(f"Data: {json.dumps(parsed_data, indent=4)}")

    return parsed_data


def install_dependencies(repo_path):
    '''Install the ruby dependencies'''
    info("Installing dependencies")
    os.system(f"cd {repo_path} && bundle install")


def name():
    return "ruby"