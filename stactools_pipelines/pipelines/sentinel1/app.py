import json
import os

import requests
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from stactools.core import use_fsspec
from stactools.sentinel1.grd import Format
from stactools.sentinel1.grd.stac import create_item

from stactools_pipelines.cognito.utils import get_token


@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context):
    ingestor_url = os.environ["INGESTOR_URL"]
    ingestions_endpoint = f"{ingestor_url.strip('/')}/ingestions"
    token = get_token()
    headers = {"Authorization": f"bearer {token}"}
    use_fsspec()
    for record in event.records:
        record_body = json.loads(record.body)
        sentinel_message = json.loads(record_body["Message"])
        href = f"s3://sentinel-s1-l1c/{sentinel_message['path']}"
        print(href)
        stac = create_item(
            granule_href=href, archive_format=Format.COG, requester_pays=True
        )
        stac.collection_id = "sentinel1-grd"
        response = requests.post(
            url=ingestions_endpoint, data=json.dumps(stac.to_dict()), headers=headers
        )
        try:
            response.raise_for_status()
        except Exception:
            print(response.text)
            raise
