import json

import pytest

import stactools_pipelines.pipelines.conftest as conftest
from stactools_pipelines.pipelines.noaa_oisst.historic import handler

pipeline_id = "noaa_oisst"
query_value = "data/v2.1/avhrr/198109/oisst-avhrr-v02r01.19810901.nc"


@pytest.mark.parametrize("pipeline_id", [pipeline_id])
@pytest.mark.parametrize("query_value", [query_value])
def test_handler(mock_env, boto3, run_query):
    query = f"SELECT key FROM {pipeline_id}.inventory where key LIKE 'data/v2.1/avhrr%'"
    handler({}, {})
    run_query.assert_called_once_with(
        conftest.athena_client, conftest.output_location, pipeline_id, query
    )

    message = {
        "Records": [
            {
                "s3": {
                    "object": {
                        "key": "data/v2.1/avhrr/198109/oisst-avhrr-v02r01.19810901.nc"
                    }
                }
            }
        ]
    }
    message_body = json.dumps({"Message": json.dumps(message)})

    conftest.sqs_client.send_message.assert_called_once_with(
        QueueUrl=conftest.queue_url, MessageBody=message_body
    )
