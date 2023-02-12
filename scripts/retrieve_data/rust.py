#!/bin/python

import requests
import json
import argparse

version="1.0.0"

# Get data for most downloaded rust packages:
def query_rust_crates_api(entries):
    # Get the most downloaded packages:
    url = f"https://crates.io/api/v1/crates?sort=downloads&page=1&per_page={entries}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error getting file")
    else:
        return response.json()

def parse_metadata_to_elasticseach_mapping(api_data):
    '''This function takes the data returned my the rust crates API and parses it to fit the elasticsearch mapping'''
    results = api_data["crates"]

    parsed_data = {}

    for result in results:

        parsed_data.update({
            result["id"]: {
                "repo_name": result["id"],
                "repo_url": result["repository"],
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