import json

import pytest

import stactools_pipelines.pipelines.conftest as conftest
from stactools_pipelines.pipelines.cop_dem_30.app import handler

key = "Copernicus_DSM_COG_10_N80_00_W104_00_DEM/Copernicus_DSM_COG_10_N80_00_W104_00_DEM.tif"


@pytest.fixture
def sns_message():
    yield key


@pytest.mark.parametrize("pipeline_id", ["cop_dem_30"])
@pytest.mark.parametrize("module", ["app"])
def test_handler(mock_env, sns_message, sqs_event, get_token, create_item, requests):
    handler(sqs_event, {})
    get_token.assert_called_once()
    create_item.assert_called_once_with(
        href=f"s3://copernicus-dem-30m/{key}", host="AWS"
    )
    requests.post.assert_called_once_with(
        url=f"{conftest.ingestor_url}/ingestions",
        data=json.dumps(conftest.item),
        headers={"Authorization": f"bearer {conftest.token}"},
    )
