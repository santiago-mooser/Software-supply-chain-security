#!/usr/bin/python


import os
from multiprocessing import Pool

import code_analysis
import git_clone
from retrieve_data import python
import elasticsearch_upload
import logging
from logging import info, debug


# If the environment variable LOG_LEVEL is set, use it to set the logging level
# otherwise, default to INFO
logging_level = os.environ.get('LOG_LEVEL', 'INFO')

logging.basicConfig(level=logging_level,
                    format='%(asctime)s - %(module)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("logs/interim.log"),
                        logging.StreamHandler()
                    ])

REPO_ELASTICSEARCH_MAPPING = {
    "mappings": {
        "properties": {
            "repo_name": {
                "type": "text",
                "index": "true"
            },
            "repo_url": {"type": "text"},
            "description": {"type": "text"},
            "version": {"type": "text"},
            "snyk_dependency_scan_results": {"type": "object"},
            "dependabot_results": {"type": "object"},
            "snyk_sast_results": {"type": "object"},
            "semgrep_results": {"type": "object"},
            "git_commit_count": {"type": "integer"},
            "git_commit_signatures_count": {"type": "integer"},
            "git_commit_signatures_percentage": {"type": "integer"},
            "package_signature": {"type": "boolan"}
        }
    }
}


api_data = python.query_api(5)

parsed_data = python.parse_metadata_to_elasticseach_mapping(api_data)

# use Pool to download git repos in parallel

p = Pool(5)

results = []

for key, value in parsed_data.items():
    path = os.path.join('/app/repos/', key)
    info(f"Cloning {key} from {value['repo_url']} into {path}")
    arguments = (value["repo_url"], path)
    results.append(p.apply_async(git_clone.clone_git_repo, args=(arguments,)))


p.close()
p.join()
info("Cloning complete")

analysis_pool = Pool(5)
# list comprehension to appent "tmp" to all keys to the keys of hte parsed_data dict
args = [(key, "/app/repos/") for key in parsed_data.keys()]
results = analysis_pool.map(code_analysis.run_analysis, args,)
analysis_pool.close()
analysis_pool.join()

info("Analysis complete")

# Put the results based on the repos into the elasticsearch mappings:

for result in results:
    for key, value in result.items():
        for k, v in value.items():
            parsed_data[key][k] = v


# upload the data to elasticsearch

settings = {
    "index": "python",
    "mapping": REPO_ELASTICSEARCH_MAPPING,
    "es_protocol": "http",
    "es_host": "elasticsearch",
    "es_port": "9200"

}

info(f"Uploading data to Elasticsearch index '{settings['index']}'")
elasticsearch_upload.upload_to_elasticsearch(parsed_data, settings)
