import json
from unittest.mock import patch

import pytest
from stactools.sentinel1.grd import Format

from aws_asdi_pipelines.pipelines.sentinel1.app import handler

sns_message = {
    "Type": "Notification",
    "MessageId": "d3f017d2-a423-531c-9151-4c357fd9f88d",
    "TopicArn": "arn:aws:sns:eu-central-1:214830741341:SentinelS1L1C",
    "Subject": "productAdded",
    "Message": '{\n  "id" : "S1A_IW_GRDH_1SDV_20221111T021759_20221111T021828_045840_057BE4_F261",\n  "path" : "GRD/2022/11/11/IW/DV/S1A_IW_GRDH_1SDV_20221111T021759_20221111T021828_045840_057BE4_F261",\n  "missionId" : "S1A",\n  "productType" : "GRD",\n  "resolution" : "H",\n  "mode" : "IW",\n  "polarization" : "DV",\n  "startTime" : "2022-11-11T02:17:59",\n  "stopTime" : "2022-11-11T02:18:28",\n  "absoluteOrbitNumber" : 45840,\n  "missionDataTakeId" : 359396,\n  "productUniqueIdentifier" : "F261",\n  "sciHubIngestion" : "2022-11-11T04:46:37.150Z",\n  "s3Ingestion" : "2022-11-11T05:12:20.424Z",\n  "sciHubId" : "b1b1b5a8-172e-4ca4-9133-56b568fac0c3",\n  "footprint" : {\n    "type" : "MultiPolygon",\n    "coordinates" : [ [ [ [ 50.659275901738766, -12.214735492727298 ], [ 50.087138870452634, -12.085621640205094 ], [ 49.51054076436727, -11.954196513607672 ], [ 48.934497012168066, -11.82160204513997 ], [ 48.41800565487764, -11.701617112544907 ], [ 48.27628473750112, -12.300171029247736 ], [ 48.19010685810016, -12.66079937267828 ], [ 48.059071273048836, -13.201399119351645 ], [ 48.0288017456064, -13.323470771719519 ], [ 48.54740381362838, -13.444908660624868 ], [ 49.125919121437335, -13.57897836247226 ], [ 49.70558847236842, -13.711836436691012 ], [ 50.285515782326186, -13.843266678550286 ], [ 50.48059742927708, -12.996532589003891 ], [ 50.659275901738766, -12.214735492727298 ] ] ] ]\n  },\n  "filenameMap" : {\n    "support/s1-level-1-calibration.xsd" : "support/s1-level-1-calibration.xsd",\n    "measurement/s1a-iw-grd-vv-20221111t021759-20221111t021828-045840-057be4-001.tiff" : "measurement/iw-vv.tiff",\n    "annotation/s1a-iw-grd-vv-20221111t021759-20221111t021828-045840-057be4-001.xml" : "annotation/iw-vv.xml",\n    "support/s1-product-preview.xsd" : "support/s1-product-preview.xsd",\n    "S1A_IW_GRDH_1SDV_20221111T021759_20221111T021828_045840_057BE4_F261.SAFE-report-20221111T044103.pdf" : "report-20221111T044103.pdf",\n    "annotation/s1a-iw-grd-vh-20221111t021759-20221111t021828-045840-057be4-002.xml" : "annotation/iw-vh.xml",\n    "support/s1-level-1-noise.xsd" : "support/s1-level-1-noise.xsd",\n    "preview/quick-look.png" : "preview/quick-look.png",\n    "manifest.safe" : "manifest.safe",\n    "annotation/calibration/noise-s1a-iw-grd-vv-20221111t021759-20221111t021828-045840-057be4-001.xml" : "annotation/calibration/noise-iw-vv.xml",\n    "preview/icons/logo.png" : "preview/icons/logo.png",\n    "annotation/rfi/rfi-s1a-iw-grd-vh-20221111t021759-20221111t021828-045840-057be4-002.xml" : "annotation/rfi/rfi-iw-vh.xml",\n    "annotation/calibration/calibration-s1a-iw-grd-vv-20221111t021759-20221111t021828-045840-057be4-001.xml" : "annotation/calibration/calibration-iw-vv.xml",\n    "annotation/calibration/calibration-s1a-iw-grd-vh-20221111t021759-20221111t021828-045840-057be4-002.xml" : "annotation/calibration/calibration-iw-vh.xml",\n    "support/s1-map-overlay.xsd" : "support/s1-map-overlay.xsd",\n    "preview/map-overlay.kml" : "preview/map-overlay.kml",\n    "annotation/rfi/rfi-s1a-iw-grd-vv-20221111t021759-20221111t021828-045840-057be4-001.xml" : "annotation/rfi/rfi-iw-vv.xml",\n    "measurement/s1a-iw-grd-vh-20221111t021759-20221111t021828-045840-057be4-002.tiff" : "measurement/iw-vh.tiff",\n    "support/s1-object-types.xsd" : "support/s1-object-types.xsd",\n    "support/s1-level-1-quicklook.xsd" : "support/s1-level-1-quicklook.xsd",\n    "preview/product-preview.html" : "preview/product-preview.html",\n    "support/s1-level-1-rfi.xsd" : "support/s1-level-1-rfi.xsd",\n    "support/s1-level-1-measurement.xsd" : "support/s1-level-1-measurement.xsd",\n    "support/s1-level-1-product.xsd" : "support/s1-level-1-product.xsd",\n    "annotation/calibration/noise-s1a-iw-grd-vh-20221111t021759-20221111t021828-045840-057be4-002.xml" : "annotation/calibration/noise-iw-vh.xml"\n  },\n  "version" : 3\n}',
    "Timestamp": "2022-11-11T05:12:26.254Z",
    "SignatureVersion": "1",
    "Signature": "rOJG/wJE7E8e1w4egShq/RuNmF5KZOP1fMw+6IzUw0qT0hj+/TSYKeTjm6raVoKXGwpZIynkIv1+GaAeyezSs+qQiwYVeOhyqWuJKc8uqJ7Hbu7xc5VChJT91jxQRcOcm4W/3lIcRkahl2KnKVc4m4Z0sl3d7PwxbPuMsa4PlMrPcHOhFVeAJUC+1FuWVqC3EryxQUvvkRU7XOM4wv6YL9CIwqC27ISY/2QgCCkCAU6yC+tfK5JHFIFZFlDfu3f8tF2juHKdnEJMKlvrKWFePKX3Lkf+l2udzo8TW5Yq7nH8liDH0ARxt19u2pduKaLqxQZzb8ry3rXw+0c2jyFKWw==",
    "SigningCertURL": "https://sns.eu-central-1.amazonaws.com/SimpleNotificationService-56e67fcb41f6fec09b0196692625d385.pem",
    "UnsubscribeURL": "https://sns.eu-central-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-central-1:214830741341:SentinelS1L1C:f402b810-3a85-47f2-9c03-19f1d9b4596d",
}
body = json.dumps(sns_message)


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
    path = json.loads(sns_message["Message"])["path"]
    create_item.assert_called_once_with(
        granule_href=f"s3://sentinel-s1-l1c/{path}",
        archive_format=Format.COG,
        requester_pays=True,
    )
