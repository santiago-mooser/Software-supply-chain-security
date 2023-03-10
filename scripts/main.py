#!/usr/bin/python

import argparse
import logging
import json
import os
from logging import debug, error, info, warning
from multiprocessing import Pool

import git_clone
from retrieve_data import javascript, python, ruby, rust
import code_analysis
import elasticsearch_upload

# This is the mapping used for elasticsearch
# Nothing interesting here
REPO_ELASTICSEARCH_MAPPING = {
    "mappings": {
        "properties": {
            "repo_name": {"type": "text", "index": "true"},
            "repo_url": {"type": "text"},
            "description": {"type": "text"},
            "version": {"type": "text"},
            "snyk_dependency_scan_results": {"type": "object"},
            "dependabot_results": {"type": "object"},
            "snyk_sast_results": {"type": "object"},
            "semgrep_results": {"type": "object"},
            "git_commit_count": {"type": "text"},
            "git_commit_signatures_count": {"type": "text"},
            "git_commit_signatures_percentage": {"type": "text"},
            "package_signature": {"type": "text"},
        }
    }
}


# Set the log level to be info by default and show which module the log is coming from
logging_level = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=logging_level,
    format="%(asctime)s - %(module)s - %(levelname)s [%(filename)s:%(lineno)s - %(funcName)20s()] - %(message)s",
    handlers=[logging.FileHandler("logs/interim.log"), logging.StreamHandler()],
)


def clone_and_analyze(settings):
    """This function clones a given git repo, run analysis scripts on it and uploads the results to elasticsearch."""

    repo_url, path, language, parsed_data = settings

    # Call the module
    language = getattr(__import__(f"retrieve_data.{language}"), language)

    # Clone the git repo
    info(f"Cloning {repo_url} into {path}...")
    git_clone.clone_git_repo(repo_url, path)

    # Run analysis scripts
    info(f"Running analysis scripts for {path}...")
    results = code_analysis.run_analysis(path, language, parsed_data)

    return results


def retrieve_data_and_run_analysis_scripts(language):
    """Retrieve data from the API and run analysis scripts in parallel."""

    results_per_language = os.environ.get("RESULTS_PER_LANGUAGE", "5")

    info(
        f"Running analysis for {language.name()}. {results_per_language} results per language."
    )

    # Retrieve data from the API
    api_data = language.query_api(results_per_language)

    # Parse the data into a format that can be uploaded to Elasticsearch
    parsed_data = language.parse_metadata_to_elasticseach_mapping(api_data)

    # use Pool to download git repos in parallel
    p = Pool(5)

    arguments = [
        (
            value["repo_url"],
            os.path.join("/app/repos/", value["repo_name"]),
            language.name(),
            value,
        )
        for repo_name, value in parsed_data.items()
    ]

    results = p.map(clone_and_analyze, arguments)

    p.close()
    p.join()

    result_dict = {}

    for result in results:
        result_dict.update(result)

    # Upload the results to Elasticsearch
    info(f"Uploading results for {language.name}...")
    elasticsearch_settings = {
        "index": language.name(),
        "mapping": REPO_ELASTICSEARCH_MAPPING,
        "es_protocol": os.environ.get("ES_PROTOCOL", "http"),
        "es_host": os.environ.get("ES_HOST", "elasticsearch"),
        "es_port": os.environ.get("ES_PORT", "9200"),
    }

    # Upload results to Elasticsearch
    info(f"Uploading results to Elasticsearch for to index {language.name()}...")
    elasticsearch_upload.upload_to_elasticsearch(result_dict, elasticsearch_settings)

    return(result_dict)


if __name__ == "__main__":

    final_results = {}

    for language in (python, ruby, rust):
        final_results.update(
            {language: retrieve_data_and_run_analysis_scripts(language)}
        )

    print(json.dumps(final_results, indent=4))
