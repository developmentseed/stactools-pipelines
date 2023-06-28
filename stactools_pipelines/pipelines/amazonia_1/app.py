"""Amazonia1 asdi handler."""

import json
import os
import re
from typing import List

import requests
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from stactools.amazonia_1 import create_item
from stactools.core import use_fsspec

from stactools_pipelines.cognito.utils import get_token


def xml_key_from_quicklook_key(key: str) -> List[str]:
    """
    Parse quicklook key and return key to INPE's metadata.

    Args:
        key: quicklook key

    Returns:
       keys to INPE's Amazonia XML
    """

    match = re.search(
        r"(?P<satellite>\w+)/(?P<camera>\w+)/"
        r"(?P<path>\d{3})/(?P<row>\d{3})/(?P<scene_id>\w+)/",
        key,
    )
    assert match, "Could not match " + key
    qdict = {
        "satellite": match.group("satellite"),
        "camera": match.group("camera"),
        "path": match.group("path"),
        "row": match.group("row"),
        "scene_id": match.group("scene_id"),
        "collection": match.group("satellite") + match.group("camera"),
    }
    metadata_key = (
        f"{qdict['satellite']}/{qdict['camera']}/{qdict['path']}/"
        f"{qdict['row']}/{qdict['scene_id']}/{qdict['scene_id']}_BAND2.xml"
    )
    keys = []
    for optics in ["", "_LEFT", "_RIGHT"]:
        keys.append(re.sub(r"_L(\d+)_", f"_L\\g<1>{optics}_", metadata_key))
    return keys


@event_source(data_class=SQSEvent)  # pylint: disable=no-value-for-parameter
def handler(event: SQSEvent, context):  # pylint: disable=unused-argument
    """Lambda entrypoint."""
    ingestor_url = os.environ["INGESTOR_URL"]
    ingestions_endpoint = f"{ingestor_url.strip('/')}/ingestions"
    use_fsspec()
    for record in event.records:
        record_body = json.loads(record.body)
        amazonia_message = json.loads(record_body["Message"])
        for rec in amazonia_message["Records"]:
            bucket = rec["s3"]["bucket"]["name"]
            png_key = rec["s3"]["object"]["key"]
            xml_keys = xml_key_from_quicklook_key(png_key)
            stac = None
            for xml_key in xml_keys:
                try:
                    href = f"s3://{bucket}/{xml_key}"
                    print(f"Trying {href}")
                    stac = create_item(asset_href=href)
                    # Stop on first option found
                    break
                except FileNotFoundError:
                    # Try next option for XML filename
                    pass
            assert stac is not None, f"XML metadata not found for {png_key}."
            stac.collection_id = "AMAZONIA1-WFI"
            response = requests.post(
                url=ingestions_endpoint,
                data=json.dumps(stac.to_dict()),
                headers={"Authorization": f"bearer {get_token()}"},
            )
            try:
                response.raise_for_status()
            except Exception:
                print(response.text)
                raise
