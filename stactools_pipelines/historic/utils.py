import logging
import time
from typing import Callable, Dict, Optional

import boto3


def run_query(client, output_location: str, database_name: str, query: str) -> str:
    """Generic function to run athena query and ensures it is successfully completed

    Parameters
    ----------
    client : A boto3 athena client
    output_location : str
        s3 location for results storage
    database_name : str
        name of Athena database to query
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


def get_current_chunk(chunk_parameter: str) -> str:
    ssm_client = boto3.client("ssm")
    response = ssm_client.get_parameter(Name=chunk_parameter)
    current_chunk = response["Parameter"]["Value"]
    return current_chunk


def set_current_chunk(chunk: str, chunk_parameter: str):
    ssm_client = boto3.client("ssm")
    ssm_client.put_parameter(Name=chunk_parameter, Value=chunk, Overwrite=True)


def queue_results(
    athena_client,
    query_id: str,
    sqs_client,
    row_processor: Callable[[Dict], Optional[str]],
    queue_url: str,
):
    results_paginator = athena_client.get_paginator("get_query_results")
    results_iter = results_paginator.paginate(
        QueryExecutionId=query_id, PaginationConfig={"PageSize": 100}
    )
    for results_page in results_iter:
        for row in results_page["ResultSet"]["Rows"]:
            body = row_processor(row)
            if body:
                print(body)
                sqs_client.send_message(QueueUrl=queue_url, MessageBody=body)
