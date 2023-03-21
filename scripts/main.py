#!/usr/bin/python

import logging
import os
from logging import debug, error, info, warning
from multiprocessing import Pool
from datetime import datetime
import json

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
            "git_commit_count": {"type": "int"},
            "git_commit_signatures_count": {"type": "int"},
            "git_commit_signatures_percentage": {"type": "int"},
            "package_signature": {"type": "text"},
        }
    }
}

DATETIME=datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

# Set the log level to be info by default and show which module the log is coming from
logging_level = os.environ.get("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=logging_level,
    format="%(asctime)s - %(module)s - %(levelname)s [%(filename)s:%(lineno)s - %(funcName)20s()] - %(message)s",
    handlers=[
        logging.FileHandler(f"logs/{DATETIME}.log"),
        logging.StreamHandler(),
    ],
)


def clone_and_analyze(settings):
    """This function clones a given git repo, run analysis scripts on it and uploads the results to elasticsearch."""

    repo_url, repo_name, language, parsed_data = settings

    # Call the module
    language = getattr(__import__(f"retrieve_data.{language}"), language)

    # Get repo path from environment
    repo_path = os.environ.get("REPO_PATH", "/tmp/repos")
    path = os.path.join(repo_path, repo_name)

    # Clone the git repo
    info(f"Cloning {repo_url} into {path}...")
    if not git_clone.clone_git_repo(repo_url, path):
        error(f"Failed to clone {repo_url} into {path}. Skipping analysis...")
        return {}

    # Run analysis scripts
    info(f"Running analysis scripts for {path}...")
    results = code_analysis.run_analysis(path, language, parsed_data)

    return {repo_name: results}


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
    num_of_threads = int(os.environ.get("NUM_OF_THREADS", 12))
    p = Pool(num_of_threads)

    arguments = [
        (
            value["repo_url"],
            repo_name,
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

    return result_dict


if __name__ == "__main__":

    final_results = {}

    for language in (javascript,python, rust, ruby):
        final_results.update(
            {language: retrieve_data_and_run_analysis_scripts(language)}
        )

    # print out the final results to a file named {DATETIME}_results.json
    file_name = f"logs/{DATETIME}_results.json"

    #print results to file
    with open(file_name, 'w') as outfile:
        json.dump(json.dumps(final_results, indent=4), outfile)

