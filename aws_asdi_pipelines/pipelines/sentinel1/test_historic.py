import os
from unittest.mock import MagicMock, patch

from aws_asdi_pipelines.pipelines.sentinel1.historic import handler

output_location = "s3://output_location"
queue_url = "queue_url"
pipeline = "sentinel1"
chunk_parameter = "chunk_parameter"

athena_client = MagicMock()
sqs_client = MagicMock()


def side_effect(client_type: str) -> MagicMock:
    if client_type == "athena":
        return athena_client
    if client_type == "sqs":
        return sqs_client


@patch.dict(os.environ, {"OUTPUT_LOCATION": output_location})
@patch.dict(os.environ, {"QUEUE_URL": queue_url})
@patch.dict(os.environ, {"CHUNK_PARAMETER": chunk_parameter})
@patch("aws_asdi_pipelines.pipelines.sentinel1.historic.set_current_chunk")
@patch("aws_asdi_pipelines.pipelines.sentinel1.historic.get_current_chunk")
@patch("aws_asdi_pipelines.pipelines.sentinel1.historic.run_query")
@patch("aws_asdi_pipelines.pipelines.sentinel1.historic.boto3")
def test_handler(boto3, run_query, get_current_chunk, set_current_chunk):
    boto3.client = MagicMock(side_effect=side_effect)
    chunk = "2022-04-20"
    query_id = "id"
    get_current_chunk.return_value = chunk
    run_query.return_value = query_id
    query = "SELECT key FROM sentinel1.inventory where key LIKE '%2022/4/20%manifest%'"

    query_value = "/test/manifest.safe"
    page = {"ResultSet": {"Rows": [{"Data": [{"VarCharValue": query_value}]}]}}
    paginator = MagicMock()
    paginator.paginate.return_value = iter((page,))
    athena_client.get_paginator.return_value = paginator

    handler({}, {})

    run_query.assert_called_once_with(athena_client, output_location, pipeline, query)

    sqs_client.send_message.assert_called_once_with(
        QueueUrl=queue_url, MessageBody='{"Message": "{\\"path\\": \\"/test\\"}"}'
    )
    set_current_chunk.assert_called_once_with("2022-04-19", chunk_parameter)
