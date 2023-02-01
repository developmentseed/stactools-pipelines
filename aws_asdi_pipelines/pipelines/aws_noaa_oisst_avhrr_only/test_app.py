import json
import os
from unittest.mock import patch

import pystac

from aws_asdi_pipelines.pipelines.aws_noaa_oisst_avhrr_only.app import (
    create_stac,
    handler,
)

domain = "domain"
client_secret = "client_secret"
client_id = "client_id"
scope = "scope"
ingestor_url = "ingestor_url"


def test_create_stac():
    item = create_stac(collection=False)
    assert type(item) == pystac.item.Item


@patch.dict(os.environ, {"DOMAIN": domain})
@patch.dict(os.environ, {"CLIENT_SECRET": client_secret})
@patch.dict(os.environ, {"CLIENT_ID": client_id})
@patch.dict(os.environ, {"SCOPE": scope})
@patch.dict(os.environ, {"INGESTOR_URL": ingestor_url})
@patch("aws_asdi_pipelines.pipelines.aws_noaa_oisst_avhrr_only.app.create_stac")
@patch("aws_asdi_pipelines.pipelines.aws_noaa_oisst_avhrr_only.app.requests")
@patch("aws_asdi_pipelines.pipelines.aws_noaa_oisst_avhrr_only.app.get_token")
def test_handler(get_token, requests, create_stac):
    token = "token"
    item = {"id": "id"}
    create_stac.return_value.to_dict.return_value = item
    get_token.return_value = token
    handler({}, {})
    get_token.assert_called_once_with(
        domain=domain, client_secret=client_secret, client_id=client_id, scope=scope
    )
    requests.post.assert_called_once_with(
        url=ingestor_url,
        data=json.dumps(item),
        headers={"Authorization": f"bearer {token}"},
    )
