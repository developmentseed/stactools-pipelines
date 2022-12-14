import os

import boto3
import yaml

from aws_asdi_pipelines.models.pipeline import Pipeline


def pipeline_config() -> str:
    PIPELINE_NAME = os.environ["PIPELINE"]
    with open(f"./aws_asdi_pipelines/pipelines/{PIPELINE_NAME}/config.yaml") as f:
        config = yaml.safe_load(f)
        pipeline = Pipeline(**config)

        return pipeline.inventory_location


def inventory_data(inventory: str) -> list:
    inventory = inventory.split("/", 3)
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=inventory[2], Key=inventory[3])
    data = response["Body"].read().decode("utf-8").splitlines()

    return data


def handler(event, context):
    QUEUE_URL = os.environ["QUEUE_URL"]
    inventory_location = pipeline_config()
    print(inventory_location)
    if inventory_location:
        keys = inventory_data(inventory_location)
        sqs_client = boto3.client("sqs")
        for key in keys:
            sqs_client.send_message(QueueUrl=QUEUE_URL, MessageBody=key)
