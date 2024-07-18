import json
import os

import requests
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from stactools.core import use_fsspec
from stactools.noaa_hrrr.constants import COLLECTION_ID_FORMAT
from stactools.noaa_hrrr.metadata import parse_href
from stactools.noaa_hrrr.stac import create_item

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
            key = sns_record["s3"]["object"]["key"]
            bucket = sns_record["s3"]["bucket"]["name"]
            path = f"https://{bucket}.s3.amazonaws.com/{key.lstrip('/')}"
            href_parsed = parse_href(path)

            if not href_parsed:
                if path.endswith(".idx"):
                    print(f"{path} is a .idx file... skipping!")
                else:
                    print(
                        f"stactools.noaa_hrrr.metadata.parse_href cannot parse this href: {path}"
                    )
                continue

            print(path)
            stac = create_item(**href_parsed)

            stac.collection_id = COLLECTION_ID_FORMAT.format(
                product=href_parsed["product"].value,
                region=href_parsed["region"].value,
            )
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
