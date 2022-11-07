import json

import pytest

bucket_name = "test_name"
key = "test_key"

s3_event = {
    "Records": [
        {
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-2",
            "eventTime": "2019-09-03T19:37:27.192Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {"principalId": "AWS:AIDAINPONIXQXHT3IKHL2"},
            "requestParameters": {"sourceIPAddress": "205.255.255.255"},
            "responseElements": {
                "x-amz-request-id": "D82B88E5F771F645",
                "x-amz-id-2": "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo=",
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "828aa6fc-f7b5-4305-8584-487c791949c1",
                "bucket": {
                    "name": bucket_name,
                    "ownerIdentity": {"principalId": "A3I5XTEXAMAI3E"},
                    "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df",
                },
                "object": {
                    "key": key,
                    "size": 1305107,
                    "eTag": "b21b84d653bb07b05b1e6b33684dc11b",
                    "sequencer": "0C0F6F405D6ED209E1",
                },
            },
        }
    ]
}

message = json.dumps(s3_event)
sns_event = {
    "Records": [
        {
            "EventVersion": "1.0",
            "EventSubscriptionArn": "arn:aws:sns:us-east-2:123456789012:sns-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
            "EventSource": "aws:sns",
            "Sns": {
                "SignatureVersion": "1",
                "Timestamp": "2019-01-02T12:45:07.000Z",
                "Signature": "tcc6faL2yUC6dgZdmrwh1Y4cGa/ebXEkAi6RibDsvpi+tE/1+82j...65r==",
                "SigningCertUrl": "https://sns.us-east-2.amazonaws.com/SimpleNotificationService-ac565b8b1a6c5d002d285f9598aa1d9b.pem",
                "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
                "Message": message,
                "MessageAttributes": {
                    "Test": {"Type": "String", "Value": "TestString"},
                    "TestBinary": {"Type": "Binary", "Value": "TestBinary"},
                },
                "Type": "Notification",
                "UnsubscribeUrl": "https://sns.us-east-2.amazonaws.com/?Action=Unsubscribe&amp;SubscriptionArn=arn:aws:sns:us-east-2:123456789012:test-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
                "TopicArn": "arn:aws:sns:us-east-2:123456789012:sns-lambda",
                "Subject": "TestInvoke",
            },
        }
    ]
}
body = json.dumps(sns_event)

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
            "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
            "awsRegion": "us-east-2",
        },
    ]
}


@pytest.fixture(autouse=True)
def sqs_event():
    return sqs_message
