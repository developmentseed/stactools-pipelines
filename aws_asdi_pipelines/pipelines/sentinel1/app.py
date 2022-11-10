import json

from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from stactools.sentinel1.grd.stac import create_item


@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context):
    for record in event.records:
        sentinel_message = json.loads(record.body)
        href = f"s3://sentinel-s1-l1c/{sentinel_message['path']}"
        print(href)
        create_item(granule_href=href)
