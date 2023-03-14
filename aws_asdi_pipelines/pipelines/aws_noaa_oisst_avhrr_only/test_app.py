import json
import os
from unittest.mock import MagicMock, call, patch

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
item = {"id": "id"}
stac_collection = {"id": "collection"}


def create_stac_return(collection: bool):
    mock = MagicMock()
    if collection:
        mock.to_dict.return_value = stac_collection
    else:
        mock.to_dict.return_value = item
    return mock


def test_create_stac():
    item = create_stac(collection=False)
    assert type(item) == pystac.item.Item


@patch.dict(os.environ, {"DOMAIN": domain})
@patch.dict(os.environ, {"CLIENT_SECRET": client_secret})
@patch.dict(os.environ, {"CLIENT_ID": client_id})
@patch.dict(os.environ, {"SCOPE": scope})
@patch.dict(os.environ, {"INGESTOR_URL": ingestor_url})
@patch(
    "aws_asdi_pipelines.pipelines.aws_noaa_oisst_avhrr_only.app.create_stac",
    side_effect=create_stac_return,
)
@patch("aws_asdi_pipelines.pipelines.aws_noaa_oisst_avhrr_only.app.requests")
@patch("aws_asdi_pipelines.pipelines.aws_noaa_oisst_avhrr_only.app.get_token")
def test_handler(get_token, requests, create_stac):
    token = "token"
    get_token.return_value = token
    handler({}, {})
    get_token.assert_called_once_with(
        domain=domain, client_secret=client_secret, client_id=client_id, scope=scope
    )
    collections_call = call(
        url=f"{ingestor_url}/collections",
        data=json.dumps(stac_collection),
        headers={"Authorization": f"bearer {token}"},
    )
    item_call = call(
        url=f"{ingestor_url}/ingestor",
        data=json.dumps(item),
        headers={"Authorization": f"bearer {token}"},
    )
    requests.post.assert_has_calls([collections_call, item_call], any_order=True)
