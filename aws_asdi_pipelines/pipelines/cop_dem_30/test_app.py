import json

import pytest

import aws_asdi_pipelines.pipelines.conftest as conftest
from aws_asdi_pipelines.pipelines.cop_dem_30.app import handler

key = "Copernicus_DSM_COG_10_N80_00_W104_00_DEM/Copernicus_DSM_COG_10_N80_00_W104_00_DEM.tif"


@pytest.fixture()
def sqs_cop_dem_30_event():
    sqs_message = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": key,
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {},
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
                "awsRegion": "us-east-2",
            },
        ]
    }
    return sqs_message


@pytest.mark.parametrize("pipeline_id", ["cop_dem_30"])
@pytest.mark.parametrize("module", ["app"])
def test_handler(mock_env, get_token, create_item, requests, sqs_cop_dem_30_event):
    handler(sqs_cop_dem_30_event, {})
    get_token.assert_called_once()
    create_item.assert_called_once_with(
        href=f"s3://copernicus-dem-30m/{key}", host="AWS"
    )
    requests.post.assert_called_once_with(
        url=conftest.ingestor_url,
        data=json.dumps(conftest.item),
        headers={"Authorization": f"bearer {conftest.token}"},
    )
