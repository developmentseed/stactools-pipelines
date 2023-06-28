"""Amazonia1 test."""

import json

import pytest

from stactools_pipelines.pipelines import conftest
from stactools_pipelines.pipelines.amazonia_1.app import (
    handler,
    xml_key_from_quicklook_key,
)

KEY = "AMAZONIA1/WFI/035/020/AMAZONIA_1_WFI_20220814_035_020_L4/AMAZONIA_1_WFI_20220814_035_020.png"


def test_xml_key_from_quicklook_key():
    """test_xml_key_from_quicklook_key."""
    # Amazonia1 case

    xml_key = xml_key_from_quicklook_key(key=KEY)
    assert xml_key == [
        "AMAZONIA1/WFI/035/020/"
        "AMAZONIA_1_WFI_20220814_035_020_L4/"
        "AMAZONIA_1_WFI_20220814_035_020_L4_BAND2.xml",
        "AMAZONIA1/WFI/035/020/"
        "AMAZONIA_1_WFI_20220814_035_020_L4/"
        "AMAZONIA_1_WFI_20220814_035_020_L4_LEFT_BAND2.xml",
        "AMAZONIA1/WFI/035/020/"
        "AMAZONIA_1_WFI_20220814_035_020_L4/"
        "AMAZONIA_1_WFI_20220814_035_020_L4_RIGHT_BAND2.xml",
    ]


@pytest.mark.parametrize("pipeline_id", ["amazonia_1"])
@pytest.mark.parametrize("module", ["app"])
@pytest.mark.parametrize("bucket", ["amazonia-pds"])
@pytest.mark.parametrize("key", [KEY])
def test_handler(
    mock_env,  # pylint: disable=unused-argument
    sqs_event,
    get_token,
    create_item,
    requests,
):
    """test_handler."""
    handler(event=sqs_event, context={})
    get_token.assert_called_once()
    create_item.assert_called_once_with(
        asset_href="s3://amazonia-pds/AMAZONIA1/WFI/035/020/"
        "AMAZONIA_1_WFI_20220814_035_020_L4/AMAZONIA_1_WFI_20220814_035_020_L4_BAND2.xml"
    )
    requests.post.assert_called_once_with(
        url=f"{conftest.ingestor_url}/ingestions",
        data=json.dumps(conftest.item),
        headers={"Authorization": f"bearer {conftest.token}"},
    )
