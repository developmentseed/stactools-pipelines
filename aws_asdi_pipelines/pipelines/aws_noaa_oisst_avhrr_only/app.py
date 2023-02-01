import json
import os

import fsspec
import pystac
import requests
import xarray as xr
import xstac

from aws_asdi_pipelines.cognito.utils import get_token


def create_stac(collection: bool):
    if collection:
        template_type = "collection-template.json"
    else:
        template_type = "item-template.json"
    template_file = os.path.join(os.path.dirname(__file__), template_type)
    template = json.load(open(template_file))

    url = "https://ncsa.osn.xsede.org/Pangeo/pangeo-forge/pangeo-forge/aws-noaa-oisst-feedstock/aws-noaa-oisst-avhrr-only.zarr"
    fs = fsspec.filesystem(
        "reference",
        fo=f"{url}/reference.json",
        remote_protocol="s3",
        remote_options={"anon": True},
    )
    m = fs.get_mapper("")
    ds = xr.open_dataset(m, engine="zarr", backend_kwargs={"consolidated": False})

    stac = xstac.xarray_to_stac(
        ds,
        template,
        temporal_dimension="time",
        x_dimension="lon",
        y_dimension="lat",
        reference_system="4326",
        validate=True,
    )
    stac.remove_links(pystac.RelType.SELF)
    stac.remove_links(pystac.RelType.ROOT)
    return stac


def handler(event, context):
    domain = os.environ["DOMAIN"]
    client_secret = os.environ["CLIENT_SECRET"]
    client_id = os.environ["CLIENT_ID"]
    scope = os.environ["SCOPE"]
    ingestor_url = os.environ["INGESTOR_URL"]
    token = get_token(
        domain=domain, client_secret=client_secret, client_id=client_id, scope=scope
    )
    headers = {"Authorization": f"bearer {token}"}
    item = create_stac(collection=False)
    item.collection_id = "aws-noaa-oisst-avhrr-only"
    response = requests.post(
        url=ingestor_url, data=json.dumps(item.to_dict()), headers=headers
    )
    try:
        response.raise_for_status()
    except Exception:
        print(response.text)
        raise
