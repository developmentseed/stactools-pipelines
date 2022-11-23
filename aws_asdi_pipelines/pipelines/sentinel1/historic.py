import datetime
import json
import logging
import os
import time
from typing import Dict, Optional

import boto3


def run_query(client, output_location: str, database_name: str, query: str) -> str:
    """Generic function to run athena query and ensures it is successfully completed

    Parameters
    ----------
    query : str
        formatted string containing athena sql query
    """
    start_response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": database_name},
        ResultConfiguration={
            "OutputLocation": output_location,
        },
    )
    query_id = start_response["QueryExecutionId"]

    while True:
        state = client.get_query_execution(QueryExecutionId=query_id)["QueryExecution"][
            "Status"
        ]["State"]
        if state == "RUNNING" or state == "QUEUED":
            time.sleep(10)
        else:
            break

    assert state == "SUCCEEDED", f"query state is {state}"
    logging.info(f"Query {query_id} complete")
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


def query_inventory(athena_client, last_date_string: str):
    last_date = datetime.datetime.strptime(last_date_string, "%Y-%m-%d")
    year = last_date.year
    month = str(last_date.month).lstrip()
    day = str(last_date.day).lstrip()
    OUTPUT_LOCATION = os.environ["OUTPUT_LOCATION"]
    query = f"SELECT key FROM sentinel1.inventory where key LIKE '%{year}/{month}/{day}%manifest%'"
    query_id = run_query(athena_client, OUTPUT_LOCATION, "sentinel1", query)
    return query_id


def get_current_chunk():
    ssm_client = boto3.client("ssm")
    CHUNK_PARAMETER = os.environ["CHUNK_PARAMETER"]
    response = ssm_client.get_parameter(Name=CHUNK_PARAMETER)
    current_chunk = response["Parameter"]["Value"]
    return current_chunk


def set_current_chunk(chunk: str):
    ssm_client = boto3.client("ssm")
    CHUNK_PARAMETER = os.environ["CHUNK_PARAMETER"]
    ssm_client.put_parameter(Name=CHUNK_PARAMETER, Value=chunk, Overwrite=True)


def handler(event, context):
    QUEUE_URL = os.environ["QUEUE_URL"]
    athena_client = boto3.client("athena")

    last_date_string = get_current_chunk()
    query_id = query_inventory(athena_client, last_date_string)
    results_paginator = athena_client.get_paginator("get_query_results")
    results_iter = results_paginator.paginate(
        QueryExecutionId=query_id, PaginationConfig={"PageSize": 100}
    )

    sqs_client = boto3.client("sqs")
    quit = 0
    for results_page in results_iter:
        for row in results_page["ResultSet"]["Rows"]:
            if quit < 20:
                body = row_to_message_body(row)
                if body:
                    print(body)
                    sqs_client.send_message(QueueUrl=QUEUE_URL, MessageBody=body)
                quit = quit + 1
    date_format = "%Y-%m-%d"
    new_last_date = datetime.datetime.strptime(
        last_date_string, date_format
    ) - datetime.timedelta(days=1)
    new_last_date_string = new_last_date.strftime(date_format)
    set_current_chunk(new_last_date_string)
