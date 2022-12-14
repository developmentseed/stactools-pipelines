import os
from unittest.mock import MagicMock, patch

from aws_asdi_pipelines.pipelines.cop_dem_30.historic import handler

queue_url = "queue_url"
pipeline = "cop_dem_30"
chunk_parameter = "chunk_parameter"

s3_client = MagicMock()
sqs_client = MagicMock()


def side_effect(client_type: str) -> MagicMock:
    print(client_type)
    if client_type == "s3":
        return s3_client
    if client_type == "sqs":
        return sqs_client


@patch.dict(os.environ, {"QUEUE_URL": queue_url})
@patch.dict(os.environ, {"PIPELINE": pipeline})
@patch(
    "aws_asdi_pipelines.pipelines.cop_dem_30.historic.pipeline_config",
    return_value="s3://bucket/inventory.csv",
)
@patch(
    "aws_asdi_pipelines.pipelines.cop_dem_30.historic.inventory_data",
    return_value=["key"],
)
@patch("aws_asdi_pipelines.pipelines.cop_dem_30.historic.boto3")
def test_handler(boto3, inventory_data, pipeline_config):
    boto3.client = MagicMock(side_effect=side_effect)

    handler({}, {})
    pipeline_config.assert_called_once_with()
    inventory_data.assert_called_once_with("s3://bucket/inventory.csv")

    sqs_client.send_message.assert_called_once_with(
        QueueUrl=queue_url,
        MessageBody="key",
    )
