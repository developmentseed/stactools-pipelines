import json

import pystac
import pytest

import stactools_pipelines.pipelines.conftest as conftest
from stactools_pipelines.pipelines.aws_noaa_oisst_avhrr_only.app import (
    create_item as module_create_item,
)
from stactools_pipelines.pipelines.aws_noaa_oisst_avhrr_only.app import handler


def test_create_item():
    item = module_create_item()
    assert type(item) == pystac.item.Item


@pytest.mark.parametrize("pipeline_id", ["aws_noaa_oisst_avhrr_only"])
@pytest.mark.parametrize("module", ["app"])
def test_handler(mock_env, get_token, create_item, requests):
    token = "token"
    get_token.return_value = token
    handler({}, {})
    get_token.assert_called_once()
    requests.post.assert_called_once_with(
        url=f"{conftest.ingestor_url}/ingestions",
        data=json.dumps(conftest.item),
        headers={"Authorization": f"bearer {conftest.token}"},
    )
