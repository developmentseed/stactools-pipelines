import json

import pytest
from stactools.sentinel1.grd import Format

from stactools_pipelines.pipelines import conftest
from stactools_pipelines.pipelines.sentinel1.app import handler

path = "GRD/2022/11/11/IW/DV/S1A_IW_GRDH_1SDV_20221111T021759_20221111T021828_045840_057BE4_F261"


@pytest.fixture
def sns_message():
    sentinel_sns_message = {
        "id": "S1A_IW_GRDH_1SDV_20221111T021759_20221111T021828_045840_057BE4_F261",
        "path": path,
    }
    sns_message = {"Message": json.dumps(sentinel_sns_message)}
    body = json.dumps(sns_message)
    yield body


@pytest.mark.parametrize("pipeline_id", ["sentinel1"])
@pytest.mark.parametrize("module", ["app"])
def test_handler(mock_env, sns_message, sqs_event, get_token, create_item, requests):
    handler(sqs_event, {})
    get_token.assert_called_once()
    create_item.assert_called_once_with(
        granule_href=f"s3://sentinel-s1-l1c/{path}",
        archive_format=Format.COG,
        requester_pays=True,
    )
    requests.post.assert_called_once_with(
        url=f"{conftest.ingestor_url}/ingestions",
        data=json.dumps(conftest.item),
        headers={"Authorization": f"bearer {conftest.token}"},
    )
