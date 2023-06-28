import json

import pytest

from stactools_pipelines.pipelines import conftest
from stactools_pipelines.pipelines.noaa_oisst.app import handler

bucket = "noaa-cdr-sea-surface-temp-optimum-interpolation-pds"
key = "data/v2.1/avhrr/198109/oisst-avhrr-v02r01.19810901.nc"


@pytest.mark.parametrize("bucket", [bucket])
@pytest.mark.parametrize("key", [key])
@pytest.mark.parametrize("pipeline_id", ["noaa_oisst"])
@pytest.mark.parametrize("module", ["app"])
def test_handler(mock_env, sns_message, sqs_event, get_token, create_item, requests):
    handler(sqs_event, {})
    get_token.assert_called_once()
    create_item.assert_called_once_with(href=f"s3://{bucket}/{key}")
    requests.post.assert_called_once_with(
        url=f"{conftest.ingestor_url}/ingestions",
        data=json.dumps(conftest.item),
        headers={"Authorization": f"bearer {conftest.token}"},
    )
