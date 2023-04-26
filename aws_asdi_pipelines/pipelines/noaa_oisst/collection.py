import json
import os

import requests
from pystac.extensions.item_assets import ItemAssetsExtension
from stactools.noaa_cdr.sea_surface_temperature_optimum_interpolation import stac

from aws_asdi_pipelines.cognito.utils import get_token


def handler(event, context):
    domain = os.environ["DOMAIN"]
    client_secret = os.environ["CLIENT_SECRET"]
    client_id = os.environ["CLIENT_ID"]
    scope = os.environ["SCOPE"]
    ingestor_url = os.environ["INGESTOR_URL"]
    collections_endpoint = f"{ingestor_url.strip('/')}/collections"
    token = get_token(
        domain=domain, client_secret=client_secret, client_id=client_id, scope=scope
    )
    headers = {"Authorization": f"bearer {token}"}
    collection = stac.create_collection()
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
