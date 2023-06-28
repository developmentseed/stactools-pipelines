import datetime
import json
import os
from typing import Dict, Optional

import boto3

from stactools_pipelines.historic.utils import (
    get_current_chunk,
    queue_results,
    run_query,
    set_current_chunk,
)


def query_inventory(athena_client, last_date_string: str) -> str:
    OUTPUT_LOCATION = os.environ["OUTPUT_LOCATION"]
    last_date = datetime.datetime.strptime(last_date_string, "%Y-%m-%d")
    year = last_date.year
    month = str(last_date.month).lstrip()
    day = str(last_date.day).lstrip()
    query = f"SELECT key FROM sentinel1.inventory where key LIKE '%{year}/{month}/{day}%manifest%'"
    query_id = run_query(athena_client, OUTPUT_LOCATION, "sentinel1", query)
    return query_id


def row_to_message_body(row: Dict) -> Optional[str]:
    manifest = row["Data"][0]["VarCharValue"]
    path = os.path.dirname(manifest)
    if path == "":
        body = None
    else:
        message = json.dumps({"path": path})
        body = json.dumps({"Message": message})
    return body


def handler(event, context):
    CHUNK_PARAMETER = os.environ["CHUNK_PARAMETER"]
    QUEUE_URL = os.environ["QUEUE_URL"]
    athena_client = boto3.client("athena")
    last_date_string = get_current_chunk(CHUNK_PARAMETER)
    query_id = query_inventory(athena_client, last_date_string)
    sqs_client = boto3.client("sqs")
    queue_results(athena_client, query_id, sqs_client, row_to_message_body, QUEUE_URL)
    date_format = "%Y-%m-%d"
    new_last_date = datetime.datetime.strptime(
        last_date_string, date_format
    ) - datetime.timedelta(days=1)
    new_last_date_string = new_last_date.strftime(date_format)
    set_current_chunk(new_last_date_string, CHUNK_PARAMETER)
