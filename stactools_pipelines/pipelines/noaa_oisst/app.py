import json
import os

import requests
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from stactools.core import use_fsspec
from stactools.noaa_cdr.sea_surface_temperature_optimum_interpolation import constants
from stactools.noaa_cdr.sea_surface_temperature_optimum_interpolation.stac import (
    create_item,
)

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
        record_message = json.loads(record_body["Message"])
        for sns_record in record_message["Records"]:
            bucket = sns_record["s3"]["bucket"]["name"]
            key = sns_record["s3"]["object"]["key"]
            path = f"s3://{bucket}/{key.lstrip('/')}"
            print(path)
            stac = create_item(href=path)

            stac.collection_id = constants.ID
            response = requests.post(
                url=ingestions_endpoint,
                data=json.dumps(stac.to_dict()),
                headers=headers,
            )
            try:
                response.raise_for_status()
            except Exception:
                print(response.text)
                raise
