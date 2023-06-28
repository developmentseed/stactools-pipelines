import json
import os

import requests
from pystac.extensions.item_assets import ItemAssetsExtension
from stactools.noaa_cdr.sea_surface_temperature_optimum_interpolation.stac import (
    create_collection,
)

from stactools_pipelines.cognito.utils import get_token


def handler(event, context):
    ingestor_url = os.environ["INGESTOR_URL"]
    collections_endpoint = f"{ingestor_url.strip('/')}/collections"
    token = get_token()
    headers = {"Authorization": f"bearer {token}"}
    collection = create_collection()
    item_assets_extension = ItemAssetsExtension(collection)

    # We only have the netcdf assets in our collection.
    item_assets_extension.item_assets = dict(
        (key, asset)
        for key, asset in item_assets_extension.item_assets.items()
        if key == "netcdf"
    )
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
