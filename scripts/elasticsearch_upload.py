#!/bin/python

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
import tqdm
import logging


logger = logging.getLogger()
warning = logger.warning
info = logger.info
debug = logger.debug
error = logger.error


def connect_to_server(protocol, host, port):
    """Connects to the Elasticsearch server."""
    client = Elasticsearch(hosts=[f"{protocol}://{host}:{port}"])
    return client


def create_index(client, settings):
    info(f"Creating an index {settings['index']}")
    """Creates an index in Elasticsearch if one isn't already there."""
    result = client.indices.create(
        index=settings["index"],
        body={
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            "mappings": settings["mapping"],
        },
        ignore=400,
    )
    return result

def generate_actions(dataset):
    for _, repo_metadata in dataset.items():
        yield repo_metadata


def upload_to_elasticsearch(data, settings):

    info(f"Connecting to Elasticsearch cluster at {settings['es_protocol']}://{settings['es_host']}:{settings['es_port']}")
    client = connect_to_server(settings["es_protocol"], settings["es_host"], settings["es_port"])

    result = create_index(client, settings)

    info(result)

    info(f"Uploading data to Elasticsearch index {settings['index']}")
    progress = tqdm.tqdm(unit="docs", total=len(data))
    successes = 0
    for ok, action in streaming_bulk(client=client, index=settings["index"], actions=generate_actions(data), raise_on_error=False, raise_on_exception=False, chunk_size=1000, request_timeout=60):
        progress.update(1)
        successes += ok
    info(f"Indexed {successes}/{len(data)} documents to Elasticsearch index {settings['index']}")
