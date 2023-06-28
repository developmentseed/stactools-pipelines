import json
import os

import requests
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from stactools.cop_dem.stac import create_item
from stactools.core import use_fsspec

from stactools_pipelines.cognito.utils import get_token


@event_source(data_class=SQSEvent)
def handler(event: SQSEvent, context):
    ingestor_url = os.environ["INGESTOR_URL"]
    ingestions_endpoint = f"{ingestor_url.strip('/')}/ingestions"
    token = get_token()
    headers = {"Authorization": f"bearer {token}"}
    use_fsspec()
    for record in event.records:
        key = record["body"]
        path = f"s3://copernicus-dem-30m/{key}"
        print(path)
        stac = create_item(href=path, host="AWS")
        stac.collection_id = "cop-dem-glo-30"

        response = requests.post(
            url=ingestions_endpoint, data=json.dumps(stac.to_dict()), headers=headers
        )
        try:
            response.raise_for_status()
        except Exception:
            print(response.text)
            raise
