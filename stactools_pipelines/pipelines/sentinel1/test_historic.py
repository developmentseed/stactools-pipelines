import json

import pytest

import stactools_pipelines.pipelines.conftest as conftest
from stactools_pipelines.pipelines.sentinel1.historic import handler

pipeline_id = "sentinel1"
chunk_parameter = "chunk_parameter"
chunk_value = "2022-04-20"
query_value = "/test/manifest.safe"


@pytest.fixture
def mock_chunk_env(monkeypatch):
    monkeypatch.setenv("CHUNK_PARAMETER", chunk_parameter)


@pytest.mark.parametrize("pipeline_id", [pipeline_id])
@pytest.mark.parametrize("query_value", [query_value])
@pytest.mark.parametrize("chunk_value", [chunk_value])
def test_handler(
    mock_env, mock_chunk_env, boto3, run_query, get_current_chunk, set_current_chunk
):
    query = "SELECT key FROM sentinel1.inventory where key LIKE '%2022/4/20%manifest%'"
    handler({}, {})

    run_query.assert_called_once_with(
        conftest.athena_client, conftest.output_location, pipeline_id, query
    )
    message = {"path": "/test"}
    message_body = json.dumps({"Message": json.dumps(message)})
    conftest.sqs_client.send_message.assert_called_once_with(
        QueueUrl=conftest.queue_url, MessageBody=message_body
    )
    set_current_chunk.assert_called_once_with("2022-04-19", chunk_parameter)
