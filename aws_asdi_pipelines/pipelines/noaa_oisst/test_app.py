import json
import os
from unittest.mock import patch

import pytest

from aws_asdi_pipelines.pipelines.noaa_oisst.app import handler

sns_message = {
    "Type": "Notification",
    "MessageId": "e7beb21e-cc51-520e-b7fe-eeb480bf5670",
    "TopicArn": "arn:aws:sns:us-east-1:709902155096:NewCDRNDVIObject",
    "Subject": "Amazon S3 Notification",
    "Message": '{"Records":[{"eventVersion":"2.1","eventSource":"aws:s3","awsRegion":"us-east-1","eventTime":"2023-04-07T16:54:05.487Z","eventName":"ObjectCreated:Put","userIdentity":{"principalId":"***"},"requestParameters":{"sourceIPAddress":"***"},"responseElements":{"x-amz-request-id":"***","x-amz-id-2":"***"},"s3":{"s3SchemaVersion":"1.0","configurationId":"7aa2472f-d0f4-46d2-a66b-a49db507bc56","bucket":{"name":"noaa-cdr-sea-surface-temp-optimum-interpolation-pds","ownerIdentity":{"principalId":"A1FTB9C2R32E6T"},"arn":"arn:aws:s3:::noaa-cdr-sea-surface-temp-optimum-interpolation-pds"},"object":{"key":"data/v2.1/avhrr/198109/oisst-avhrr-v02r01.19810901.nc","size":31608,"eTag":"d79ac208ff860690b5ec71b28794652e","sequencer":"0064304AAD6C368992"}}}]}',
    "Timestamp": "2023-04-07T16:54:06.400Z",
    "SignatureVersion": "1",
    "Signature": "nK6FSyqZXRTxp8NW6eOXb0It05Gz2Y4ZRUHDUq+bTiSuC6YFnMsHeAywat2BkH4LNt/SENxcPkUAtsSn4KI2kRWLq0njBxDBAosW8z+JbE+qhzPnbRzsIXbLSHyN8ZRV0VTL1T55QH1fibNCpLe0tj6+Vm38qC57oYOYhiLLXJdPNKzKj1QVGDFx+Z+a8nKxACiQ94+DnlNQ+1Gj4+aHbTmdzxcUpeMjyL3t6y9Oiu3bMgR6XkKVHKx+nycrwVKpkPZZLxC8Wq1+3Z7UmKAkic5ooGURArycGEatcqCRzzovowHd5+l31nQFRrrDGtt7j2yIXm9AcJskHSfFBxYb9Q==",
    "SigningCertURL": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-56e67fcb41f6fec09b0196692625d385.pem",
    "UnsubscribeURL": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:709902155096:NewCDRNDVIObject:63acafcc-4ff3-4b64-9cc4-c559c23391b8",
}
body = json.dumps(sns_message)


@pytest.fixture()
def sqs_noaa_oisst_event():
    sqs_message = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": body,
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
@patch("aws_asdi_pipelines.pipelines.noaa_oisst.app.requests")
@patch("aws_asdi_pipelines.pipelines.noaa_oisst.app.get_token")
@patch("aws_asdi_pipelines.pipelines.noaa_oisst.app.create_item")
def test_handler(create_item, get_token, requests, sqs_noaa_oisst_event):
    token = "token"
    item = {"id": "id"}
    create_item.return_value.to_dict.return_value = item
    get_token.return_value = token
    handler(sqs_noaa_oisst_event, {})
    get_token.assert_called_once_with(
        domain=domain, client_secret=client_secret, client_id=client_id, scope=scope
    )
    path = json.loads(sns_message["Message"])["Records"][0]["s3"]["object"]["key"]
    print(path)
    create_item.assert_called_once_with(
        href=f"s3://noaa-cdr-sea-surface-temp-optimum-interpolation-pds/{path}"
    )
    requests.post.assert_called_once_with(
        url=f"{ingestor_url}/ingestions",
        data=json.dumps(item),
        headers={"Authorization": f"bearer {token}"},
    )
