import json

from aws_lambda_powertools.utilities.data_classes import (
    SQSEvent,
    S3Event,
    SNSEvent,
    event_source,
)
import stactools


@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context):
    for record in event.records:
        sns_event = SNSEvent(json.loads(record.body))
        sns_message = sns_event.record.sns
        s3event = S3Event(json.loads(sns_message.message))
        s3object = s3event.record.s3.get_object
        href = f"s3://{s3event.bucket_name}/{s3object.key}"
        stac = stactools.sentinel1.grd.stac.create_item(granule_href=href)
        print(stac)
