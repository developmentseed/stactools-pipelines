import os
from unittest.mock import MagicMock, patch

from aws_asdi_pipelines.pipelines.cop_dem_30.historic import handler

output_location = "s3://output_location"
queue_url = "queue_url"
pipeline = "cop_dem_30"
chunk_parameter = "chunk_parameter"

athena_client = MagicMock()
sqs_client = MagicMock()


def side_effect(client_type: str) -> MagicMock:
    if client_type == "athena":
        return athena_client
    if client_type == "sqs":
        return sqs_client


@patch.dict(os.environ, {"OUTPUT_LOCATION": output_location})
@patch.dict(os.environ, {"QUEUE_URL": queue_url})
@patch("aws_asdi_pipelines.pipelines.cop_dem_30.historic.run_query")
@patch("aws_asdi_pipelines.pipelines.cop_dem_30.historic.boto3")
def test_handler(boto3, run_query):
    boto3.client = MagicMock(side_effect=side_effect)
    query_id = "id"
    run_query.return_value = query_id
    query = "SELECT key FROM cop_dem_30.inventory"

    query_value = "Copernicus_DSM_COG_10_N80_00_W104_00_DEM/Copernicus_DSM_COG_10_N80_00_W104_00_DEM.tif"
    page = {"ResultSet": {"Rows": [{"Data": [{"VarCharValue": query_value}]}]}}
    paginator = MagicMock()
    paginator.paginate.return_value = iter((page,))
    athena_client.get_paginator.return_value = paginator

    handler({}, {})

    run_query.assert_called_once_with(athena_client, output_location, pipeline, query)

    sqs_client.send_message.assert_called_once_with(
        QueueUrl=queue_url,
        MessageBody='{"Message": "{\\"path\\": \\"Copernicus_DSM_COG_10_N80_00_W104_00_DEM\\"}"}',
    )
