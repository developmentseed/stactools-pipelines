import json
from unittest.mock import patch

import pytest

from aws_asdi_pipelines.pipelines.sentinel1.app import handler

body = '{\n  "id" : "S1A_IW_GRDH_1SDV_20221108T222932_20221108T223005_045809_057AD9_A24E",\n  "path" : "GRD/2022/11/8/IW/DV/S1A_IW_GRDH_1SDV_20221108T222932_20221108T223005_045809_057AD9_A24E",\n  "missionId" : "S1A",\n  "productType" : "GRD",\n  "resolution" : "H",\n  "mode" : "IW",\n  "polarization" : "DV",\n  "startTime" : "2022-11-08T22:29:32",\n  "stopTime" : "2022-11-08T22:30:05",\n  "absoluteOrbitNumber" : 45809,\n  "missionDataTakeId" : 359129,\n  "productUniqueIdentifier" : "A24E",\n  "sciHubIngestion" : "2022-11-09T01:12:48.161Z",\n  "s3Ingestion" : "2022-11-09T01:42:49.262Z",\n  "sciHubId" : "90398f3d-5431-49a2-ae7b-43130aa47c37",\n  "footprint" : {\n    "type" : "MultiPolygon",\n    "coordinates" : [ [ [ [ -66.50351644628294, 20.325616447559376 ], [ -65.9153112716784, 20.43369464484065 ], [ -65.32167456654572, 20.54060725867992 ], [ -64.72722062179503, 20.64548709183752 ], [ -64.13696627342593, 20.747463040466926 ], [ -64.49728172350588, 22.60180118222781 ], [ -65.09536478948601, 22.50110928695777 ], [ -65.69763235771046, 22.3973210240898 ], [ -66.29899766500023, 22.29129668604465 ], [ -66.89478407962521, 22.183899535391404 ], [ -66.69390227117161, 21.231879978341933 ], [ -66.50351644628294, 20.325616447559376 ] ] ] ]\n  },\n  "filenameMap" : {\n    "support/s1-level-1-calibration.xsd" : "support/s1-level-1-calibration.xsd",\n    "support/s1-product-preview.xsd" : "support/s1-product-preview.xsd",\n    "measurement/s1a-iw-grd-vh-20221108t222932-20221108t223005-045809-057ad9-002.tiff" : "measurement/iw-vh.tiff",\n    "annotation/s1a-iw-grd-vv-20221108t222932-20221108t223005-045809-057ad9-001.xml" : "annotation/iw-vv.xml",\n    "support/s1-level-1-noise.xsd" : "support/s1-level-1-noise.xsd",\n    "preview/quick-look.png" : "preview/quick-look.png",\n    "manifest.safe" : "manifest.safe",\n    "S1A_IW_GRDH_1SDV_20221108T222932_20221108T223005_045809_057AD9_A24E.SAFE-report-20221109T010803.pdf" : "report-20221109T010803.pdf",\n    "preview/icons/logo.png" : "preview/icons/logo.png",\n    "annotation/rfi/rfi-s1a-iw-grd-vv-20221108t222932-20221108t223005-045809-057ad9-001.xml" : "annotation/rfi/rfi-iw-vv.xml",\n    "support/s1-map-overlay.xsd" : "support/s1-map-overlay.xsd",\n    "annotation/calibration/calibration-s1a-iw-grd-vh-20221108t222932-20221108t223005-045809-057ad9-002.xml" : "annotation/calibration/calibration-iw-vh.xml",\n    "annotation/calibration/calibration-s1a-iw-grd-vv-20221108t222932-20221108t223005-045809-057ad9-001.xml" : "annotation/calibration/calibration-iw-vv.xml",\n    "preview/map-overlay.kml" : "preview/map-overlay.kml",\n    "annotation/calibration/noise-s1a-iw-grd-vv-20221108t222932-20221108t223005-045809-057ad9-001.xml" : "annotation/calibration/noise-iw-vv.xml",\n    "annotation/calibration/noise-s1a-iw-grd-vh-20221108t222932-20221108t223005-045809-057ad9-002.xml" : "annotation/calibration/noise-iw-vh.xml",\n    "preview/product-preview.html" : "preview/product-preview.html",\n    "support/s1-level-1-quicklook.xsd" : "support/s1-level-1-quicklook.xsd",\n    "support/s1-object-types.xsd" : "support/s1-object-types.xsd",\n    "support/s1-level-1-rfi.xsd" : "support/s1-level-1-rfi.xsd",\n    "measurement/s1a-iw-grd-vv-20221108t222932-20221108t223005-045809-057ad9-001.tiff" : "measurement/iw-vv.tiff",\n    "support/s1-level-1-measurement.xsd" : "support/s1-level-1-measurement.xsd",\n    "support/s1-level-1-product.xsd" : "support/s1-level-1-product.xsd",\n    "annotation/rfi/rfi-s1a-iw-grd-vh-20221108t222932-20221108t223005-045809-057ad9-002.xml" : "annotation/rfi/rfi-iw-vh.xml",\n    "annotation/s1a-iw-grd-vh-20221108t222932-20221108t223005-045809-057ad9-002.xml" : "annotation/iw-vh.xml"\n  },\n  "version" : 3\n}'


@pytest.fixture()
def sqs_sentinel1_event():
    sqs_message = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": body,
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1545082649183",
                    "SenderId": "AIDAIENQZJOLO23YVJ4VO",
                    "ApproximateFirstReceiveTimestamp": "1545082649185",
                },
                "messageAttributes": {},
                "md5OfBody": "e4e68fb7bd0e697a0ae8f1bb342846b3",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-2:123456789012:my-queue",
                "awsRegion": "us-east-2",
            },
        ]
    }
    return sqs_message


@patch("aws_asdi_pipelines.pipelines.sentinel1.app.create_item")
def test_handler(create_item, sqs_sentinel1_event):
    handler(sqs_sentinel1_event, {})
    path = json.loads(body)["path"]
    create_item.assert_called_once_with(granule_href=f"s3://sentinel-s1-l1c/{path}")
