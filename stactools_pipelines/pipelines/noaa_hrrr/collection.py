import json
import os

import requests
from stactools.noaa_hrrr.metadata import CloudProvider, Product, Region
from stactools.noaa_hrrr.stac import create_collection

from stactools_pipelines.cognito.utils import get_token


def handler(event, context):
    ingestor_url = os.environ["INGESTOR_URL"]
    collections_endpoint = f"{ingestor_url.strip('/')}/collections"
    token = get_token()
    headers = {"Authorization": f"bearer {token}"}

    for region in Region:
        for product in Product:
            collection = create_collection(
                region=region, product=product, cloud_provider=CloudProvider.aws
            )

            response = requests.post(
                url=collections_endpoint,
                data=json.dumps(collection.to_dict()),
                headers=headers,
            )
            print(collection.id)
            print(collections_endpoint)
            try:
                response.raise_for_status()
            except Exception:
                print(response.text)
                raise
