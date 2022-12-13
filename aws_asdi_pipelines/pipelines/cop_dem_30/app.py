import json
import os

import requests
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from stactools.core import use_fsspec
from stactools.cop_dem.stac import create_item

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
        record_body = record["body"]
        path = f"s3://copernicus-dem-30m/{record_body}"
        print(path)
        stac = create_item(href=path)
        stac.collection_id = "cop-dem-glo-30"

        response = requests.post(
            url=ingestor_url, data=json.dumps(stac.to_dict()), headers=headers
        )
        try:
            response.raise_for_status()
        except Exception:
            print(response.text)
            raise
