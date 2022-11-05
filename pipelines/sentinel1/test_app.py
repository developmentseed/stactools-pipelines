from unittest.mock import MagicMock
from .app import handler
from ..fixtures.events import bucket_name, key


def test_handler(monkeypatch, sqs_event):
    create_item = MagicMock(return_value="wat")
    monkeypatch.setattr("stactools.sentinel1.grd.stac.create_item", create_item)
    handler(sqs_event, {})
    create_item.assert_called_once_with(granule_href=f"s3://{bucket_name}/{key}")
