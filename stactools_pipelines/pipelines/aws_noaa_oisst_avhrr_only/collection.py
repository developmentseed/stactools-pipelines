import json
import os

import fsspec
import pystac
import requests
import xarray as xr
import xstac

from stactools_pipelines.cognito.utils import get_token


def create_collection() -> pystac.STACObject:
    template_type = "collection-template.json"
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


def post_ingestor(stac: pystac.STACObject, url: str, headers):
    response = requests.post(url=url, data=json.dumps(stac.to_dict()), headers=headers)
    try:
        response.raise_for_status()
    except Exception:
        print(response.text)
        raise


def handler(event, context):
    ingestor_url = os.environ["INGESTOR_URL"]
    collections_endpoint = f"{ingestor_url.strip('/')}/collections"
    token = get_token()
    headers = {"Authorization": f"bearer {token}"}
    collection = create_collection()
    post_ingestor(collection, collections_endpoint, headers)
