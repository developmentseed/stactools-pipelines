import json

import pystac
import pytest

import stactools_pipelines.pipelines.conftest as conftest
from stactools_pipelines.pipelines.aws_noaa_oisst_avhrr_only.collection import (
    create_collection as module_create_collection,
)
from stactools_pipelines.pipelines.aws_noaa_oisst_avhrr_only.collection import handler


def test_create_collection():
    collection = module_create_collection()
    assert type(collection) == pystac.collection.Collection


@pytest.mark.parametrize("pipeline_id", ["aws_noaa_oisst_avhrr_only"])
@pytest.mark.parametrize("module", ["collection"])
def test_handler(mock_env, get_token, create_collection, requests):
    token = "token"
    get_token.return_value = token
    handler({}, {})
    get_token.assert_called_once()
    requests.post.assert_called_once_with(
        url=f"{conftest.ingestor_url}/collections",
        data=json.dumps(conftest.item),
        headers={"Authorization": f"bearer {conftest.token}"},
    )
