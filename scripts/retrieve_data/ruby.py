#!/bin/python
import requests
import json
import argparse

version="1.0.0"


def query_api(entries):

    # Get results from first 10 pages of ruby API:
    packages_information = []

    for page in range(0, entries//10):
        url = f"https://rubygems.org/api/v1/search.json?query=*&page={page}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error querying rubygems API for page {page}")
        else:
            packages_information += response.json()

    return packages_information


def parse_metadata_to_elasticseach_mapping(api_data):
    '''This function takes the data returned my the rubygems API and parses it to fit the elasticsearch mapping'''
    results = api_data

    parsed_data = {}

    for result in results:

        parsed_data.update({
            result["name"]: {
                "repo_name": result["name"],
                "repo_url": result["project_uri"],
                "description": result["info"],
                "version": result["version"],
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