import json
from unittest.mock import MagicMock, patch

import pytest

domain = "domain"
client_secret = "client_secret"
client_id = "client_id"
scope = "scope"
ingestor_url = "https://ingestor_url"
token = "token"
item = {"id": "id"}
collection = {"id": "id"}
output_location = "s3://output_location"
queue_url = "queue_url"
query_id = "id"

athena_client = MagicMock()
sqs_client = MagicMock()


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("DOMAIN", domain)
    monkeypatch.setenv("CLIENT_SECRET", client_secret)
    monkeypatch.setenv("CLIENT_ID", client_id)
    monkeypatch.setenv("SCOPE", scope)
    monkeypatch.setenv("INGESTOR_URL", ingestor_url)
    monkeypatch.setenv("OUTPUT_LOCATION", output_location)
    monkeypatch.setenv("QUEUE_URL", queue_url)


@pytest.fixture
def sns_message(bucket, key):
    sns_records = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": bucket, "arn": f"arn:aws:s3:::{bucket}"},
                    "object": {
                        "key": key,
                        "size": 31608,
                        "eTag": "d79ac208ff860690b5ec71b28794652e",
                        "sequencer": "0064304AAD6C368992",
                    },
                }
            }
        ]
    }

    sns_message = {"Message": json.dumps(sns_records)}
    body = json.dumps(sns_message)
    yield body


@pytest.fixture()
def sqs_event(sns_message):
    sqs_message = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": sns_message,
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {},
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:my-queue",
                "awsRegion": "us-east-1",
            },
        ]
    }
    yield sqs_message


@pytest.fixture()
def get_token(pipeline_id, module):
    with patch(
        f"stactools_pipelines.pipelines.{pipeline_id}.{module}.get_token",
        return_value=token,
        autospec=True,
    ) as m:
        yield m


@pytest.fixture()
def create_item(pipeline_id):
    with patch(
        f"stactools_pipelines.pipelines.{pipeline_id}.app.create_item",
        autospec=True,
    ) as m:
        m.return_value.to_dict.return_value = item
        yield m


@pytest.fixture()
def create_collection(pipeline_id):
    with patch(
        f"stactools_pipelines.pipelines.{pipeline_id}.collection.create_collection",
        autospec=True,
    ) as m:
        m.return_value.to_dict.return_value = collection
        yield m


@pytest.fixture()
def requests(pipeline_id, module):
    with patch(
        f"stactools_pipelines.pipelines.{pipeline_id}.{module}.requests", autospec=True
    ) as m:
        yield m


@pytest.fixture()
def run_query(pipeline_id):
    with patch(
        f"stactools_pipelines.pipelines.{pipeline_id}.historic.run_query",
        return_value=query_id,
        autospec=True,
    ) as m:
        yield m


def side_effect(client_type: str) -> MagicMock:
    if client_type == "athena":
        return athena_client
    if client_type == "sqs":
        return sqs_client


@pytest.fixture()
def boto3(pipeline_id, query_value):
    with patch(
        f"stactools_pipelines.pipelines.{pipeline_id}.historic.boto3", autospec=True
    ) as m:
        m.client = MagicMock(side_effect=side_effect)
        page = {"ResultSet": {"Rows": [{"Data": [{"VarCharValue": query_value}]}]}}
        paginator = MagicMock()
        paginator.paginate.return_value = iter((page,))
        athena_client.get_paginator.return_value = paginator
        yield m


@pytest.fixture
def get_current_chunk(pipeline_id, chunk_value):
    with patch(
        f"stactools_pipelines.pipelines.{pipeline_id}.historic.get_current_chunk",
        return_value=chunk_value,
        autospec=True,
    ) as m:
        yield m


@pytest.fixture
def set_current_chunk(pipeline_id):
    with patch(
        f"stactools_pipelines.pipelines.{pipeline_id}.historic.set_current_chunk",
        autospec=True,
    ) as m:
        yield m
