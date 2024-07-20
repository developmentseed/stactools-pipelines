import json

import pytest
from stactools.noaa_hrrr.metadata import parse_href

from stactools_pipelines.pipelines import conftest
from stactools_pipelines.pipelines.noaa_hrrr.app import handler

bucket = "noaa-hrrr-bdp-pds"
good_key = "hrrr.20140806/conus/hrrr.t00z.wrfnatf00.grib2.idx"
bad_keys = [
    "hrrr.20140806/conus/hrrr.t00z.wrfnatf00.grib2.idx",
    "hrrr.20140806/conus/hrrr.t00z.wrfnatf00.grib2",
    "hrrr.20240717/conus/hrrr.t00z.bufrsnd.tar.gz",
]


@pytest.mark.parametrize("bucket", [bucket])
@pytest.mark.parametrize("key", [good_key])
@pytest.mark.parametrize("pipeline_id", ["noaa_hrrr"])
@pytest.mark.parametrize("module", ["app"])
def test_handler(mock_env, sns_message, sqs_event, get_token, create_item, requests):
    handler(sqs_event, {})
    get_token.assert_called_once()
    grib_key = good_key[:-4]
    create_item.assert_called_once_with(
        **parse_href(f"https://{bucket}.s3.amazonaws.com/{grib_key}")
    )
    requests.post.assert_called_once_with(
        url=f"{conftest.ingestor_url}/ingestions",
        data=json.dumps(conftest.item),
        headers={"Authorization": f"bearer {conftest.token}"},
    )


@pytest.mark.parametrize("bucket", [bucket])
@pytest.mark.parametrize("key", bad_keys)
@pytest.mark.parametrize("pipeline_id", ["noaa_hrrr"])
@pytest.mark.parametrize("module", ["app"])
def test_handler_bad_keys(
    mock_env, sns_message, sqs_event, get_token, create_item, requests
):
    handler(sqs_event, {})
    get_token.assert_called_once()

    # sns_messages with keys that can't be parsed by stactools will get skipped
    create_item.assert_has_calls([], any_order=True)
    requests.post.assert_has_calls([], any_order=True)
