import json
import os

import requests
from stactools.sentinel1.grd.stac import create_collection

from stactools_pipelines.cognito.utils import get_token


def handler(event, context):
    ingestor_url = os.environ["INGESTOR_URL"]
    collections_endpoint = f"{ingestor_url.strip('/')}/collections"
    token = get_token()
    headers = {"Authorization": f"bearer {token}"}
    collection = create_collection(json_path="")
    response = requests.post(
        url=collections_endpoint, data=json.dumps(collection.to_dict()), headers=headers
    )
    print(collection.id)
    print(collections_endpoint)
    try:
        response.raise_for_status()
    except Exception:
        print(response.text)
        raise
