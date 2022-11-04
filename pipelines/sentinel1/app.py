import json

from aws_lambda_powertools.utilities.data_classes import (
    SQSEvent, S3Event, event_source
)
from aws_lambda_powertools.utilities.data_classes.sns_event import SNSMessage
from stactools.sentinel1.grd.stac import create_item


@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context):
    for record in event.records:
        sns = SNSMessage(record.body)
        s3event = S3Event(json.loads(sns.message))
        s3object = s3event.record.s3.get_object
        href = f"s3://{s3object.bucket}/{s3object.key}"

        stac = create_item(granule_href=href)
