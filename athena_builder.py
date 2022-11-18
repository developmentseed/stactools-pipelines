import logging
import os

import boto3
import yaml

from aws_asdi_pipelines.models.pipeline import Pipeline
from aws_asdi_pipelines.pipelines.athena.utils import (
    build_create_table_query,
    run_query,
)

logging.basicConfig(level=logging.INFO)
pipeline_name = os.environ["PIPELINE"]


with open(f"./aws_asdi_pipelines/pipelines/{pipeline_name}/config.yaml") as f:
    config = yaml.safe_load(f)
    pipeline = Pipeline(**config)

    if pipeline.inventory_location:
        athena_client = boto3.client("athena")
        cf_client = boto3.client("cloudformation")
        response = cf_client.describe_stacks(StackName=pipeline_name)
        outputs = response["Stacks"][0]["Outputs"]
        for output in outputs:
            keyName = output["OutputKey"]
            if keyName == "AthenaResultsBucket":
                results_location = output["OutputValue"]

        creation_location = f"s3://{results_location}/creation/"
        create_database = f"create database {pipeline_name}"
        run_query(
            athena_client,
            creation_location,
            pipeline_name,
            create_database,
            creation_location,
        )
        create_table = build_create_table_query(pipeline.inventory_location)
        run_query(
            athena_client,
            creation_location,
            pipeline_name,
            create_table,
            creation_location,
        )
