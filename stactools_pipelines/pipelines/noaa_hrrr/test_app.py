import json

import pytest
from stactools.noaa_hrrr.metadata import parse_href

from stactools_pipelines.pipelines import conftest
from stactools_pipelines.pipelines.noaa_hrrr.app import handler

bucket = "noaa-hrrr-bdp-pds"
key = "hrrr.20140806/conus/hrrr.t00z.wrfnatf00.grib2"


@pytest.mark.parametrize("bucket", [bucket])
@pytest.mark.parametrize("key", [key])
@pytest.mark.parametrize("pipeline_id", ["noaa_hrrr"])
@pytest.mark.parametrize("module", ["app"])
def test_handler(mock_env, sns_message, sqs_event, get_token, create_item, requests):
    handler(sqs_event, {})
    get_token.assert_called_once()
    create_item.assert_called_once_with(
        **parse_href(f"https://noaa-hrrr-bdp-pds.s3.amazonaws.com/{key}")
    )
    requests.post.assert_called_once_with(
        url=f"{conftest.ingestor_url}/ingestions",
        data=json.dumps(conftest.item),
        headers={"Authorization": f"bearer {conftest.token}"},
    )
