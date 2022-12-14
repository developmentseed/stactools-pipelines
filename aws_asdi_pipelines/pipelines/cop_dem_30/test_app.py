import json
import os
from unittest.mock import patch

import pytest

from aws_asdi_pipelines.pipelines.cop_dem_30.app import handler


@pytest.fixture()
def sqs_cop_dem_30_event():
    sqs_message = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": "Copernicus_DSM_COG_10_N80_00_W104_00_DEM/Copernicus_DSM_COG_10_N80_00_W104_00_DEM.tif",
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


domain = "domain"
client_secret = "client_secret"
client_id = "client_id"
scope = "scope"
ingestor_url = "ingestor_url"


@patch.dict(os.environ, {"DOMAIN": domain})
@patch.dict(os.environ, {"CLIENT_SECRET": client_secret})
@patch.dict(os.environ, {"CLIENT_ID": client_id})
@patch.dict(os.environ, {"SCOPE": scope})
@patch.dict(os.environ, {"INGESTOR_URL": ingestor_url})
@patch("aws_asdi_pipelines.pipelines.cop_dem_30.app.requests")
@patch("aws_asdi_pipelines.pipelines.cop_dem_30.app.get_token")
@patch("aws_asdi_pipelines.pipelines.cop_dem_30.app.create_item")
def test_handler(create_item, get_token, requests, sqs_cop_dem_30_event):
    token = "token"
    item = {"id": "id"}
    create_item.return_value.to_dict.return_value = item
    get_token.return_value = token
    handler(sqs_cop_dem_30_event, {})
    get_token.assert_called_once_with(
        domain=domain, client_secret=client_secret, client_id=client_id, scope=scope
    )
    path = sqs_cop_dem_30_event["Records"][0]["body"]
    print(path)
    create_item.assert_called_once_with(
        href=f"s3://copernicus-dem-30m/{path}", host="AWS"
    )
    requests.post.assert_called_once_with(
        url=ingestor_url,
        data=json.dumps(item),
        headers={"Authorization": f"bearer {token}"},
    )
