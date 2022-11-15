import json

from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from stactools.core import use_fsspec
from stactools.sentinel1.grd import Format
from stactools.sentinel1.grd.stac import create_item


@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context):
    use_fsspec()
    for record in event.records:
        record_body = json.loads(record.body)
        sentinel_message = json.loads(record_body["Message"])
        href = f"s3://sentinel-s1-l1c/{sentinel_message['path']}"
        print(href)
        stac = create_item(
            granule_href=href, archive_format=Format.COG, requester_pays=True
        )
        print(stac.to_dict())
