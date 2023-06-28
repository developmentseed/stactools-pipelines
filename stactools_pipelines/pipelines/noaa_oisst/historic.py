import json
import os
from typing import Dict, Optional

import boto3

from stactools_pipelines.historic.utils import queue_results, run_query


def query_inventory(athena_client) -> str:
    OUTPUT_LOCATION = os.environ["OUTPUT_LOCATION"]
    query = "SELECT key FROM noaa_oisst.inventory where key LIKE 'data/v2.1/avhrr%'"
    query_id = run_query(athena_client, OUTPUT_LOCATION, "noaa_oisst", query)
    return query_id


def row_to_message_body(row: Dict) -> Optional[str]:
    key = row["Data"][0]["VarCharValue"]
    if key == "":
        body = None
    else:
        message = json.dumps({"Records": [{"s3": {"object": {"key": key}}}]})
        body = json.dumps({"Message": message})
    return body


def handler(event, context):
    QUEUE_URL = os.environ["QUEUE_URL"]
    athena_client = boto3.client("athena")
    query_id = query_inventory(athena_client)
    sqs_client = boto3.client("sqs")
    queue_results(athena_client, query_id, sqs_client, row_to_message_body, QUEUE_URL)
