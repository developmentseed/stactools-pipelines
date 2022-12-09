import json
import os

import requests
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from stactools.core import use_fsspec
from stactools.sentinel1.grd import Format
from stactools.sentinel1.grd.stac import create_item

from aws_asdi_pipelines.cognito.utils import get_token


@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context):
    domain = os.environ["DOMAIN"]
    client_secret = os.environ["CLIENT_SECRET"]
    client_id = os.environ["CLIENT_ID"]
    scope = os.environ["SCOPE"]
    ingestor_url = os.environ["INGESTOR_URL"]
    token = get_token(
        domain=domain, client_secret=client_secret, client_id=client_id, scope=scope
    )
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
            url=ingestor_url, data=json.dumps(stac.to_dict()), headers=headers
        )
        try:
            response.raise_for_status()
        except Exception:
            print(response.text)
            raise
