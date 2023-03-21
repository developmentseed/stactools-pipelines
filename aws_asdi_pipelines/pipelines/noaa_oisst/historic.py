import json
import os
from typing import Dict, Optional

import boto3

from aws_asdi_pipelines.historic.utils import queue_results, run_query


def query_inventory(athena_client) -> str:
    OUTPUT_LOCATION = os.environ["OUTPUT_LOCATION"]
    query = "SELECT key FROM noaa_oisst.inventory"
    query_id = run_query(athena_client, OUTPUT_LOCATION, "noaa_oisst", query)
    return query_id


def row_to_message_body(row: Dict) -> Optional[str]:
    data_source = row["Data"][0]["VarCharValue"]
    path = os.path.dirname(data_source)
    if path == "":
        body = None
    else:
        message = json.dumps({"path": path})
        body = json.dumps({"Message": message})
    return body


def handler(event, context):
    QUEUE_URL = os.environ["QUEUE_URL"]
    athena_client = boto3.client("athena")
    query_id = query_inventory(athena_client)
    sqs_client = boto3.client("sqs")
    queue_results(athena_client, query_id, sqs_client, row_to_message_body, QUEUE_URL)
