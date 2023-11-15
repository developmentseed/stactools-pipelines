import base64
import logging
import os

import boto3
import botocore
import docker
import yaml

from stactools_pipelines.models.pipeline import Pipeline

logging.basicConfig(level=logging.DEBUG)
pipeline_name = os.environ["PIPELINE"]


def build_and_push(dockerfile: str, tag: str, pipeline_id: str):
    image, build_logs = client.images.build(
        path="./",
        dockerfile=dockerfile,
        tag=tag,
        buildargs={
            "pipeline": pipeline_id,
        },
    )
    for chunk in build_logs:
        if "stream" in chunk:
            for line in chunk["stream"].splitlines():
                logging.debug(line)

    ecr_client = boto3.client("ecr")
    try:
        ecr_client.create_repository(repositoryName=tag)
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "RepositoryAlreadyExistsException":
            logging.debug("Repository already exists")
        else:
            raise error

    ecr_credentials = ecr_client.get_authorization_token()["authorizationData"][0]

    ecr_password = (
        base64.b64decode(ecr_credentials["authorizationToken"])
        .replace(b"AWS:", b"")
        .decode("utf-8")
    )

    ecr_url = ecr_credentials["proxyEndpoint"]
    client.login(username="AWS", password=ecr_password, registry=ecr_url)
    ecr_repo_name = "{}/{}".format(ecr_url.replace("https://", ""), tag)
    image.tag(ecr_repo_name, tag="latest")
    push_log = client.images.push(ecr_repo_name, tag="latest")
    logging.debug(push_log)


with open(f"./stactools_pipelines/pipelines/{pipeline_name}/config.yaml") as f:
    config = yaml.safe_load(f)
    pipeline = Pipeline(**config)

    client = docker.from_env()
    if pipeline.compute == "awslambda":
        dockerfile = "./lambda.collection.Dockerfile"
        tag = f"{pipeline.id}-collection"
        build_and_push(dockerfile, tag, pipeline.id)

        dockerfile = "./lambda.Dockerfile"
        tag = pipeline.id
        build_and_push(dockerfile, tag, pipeline.id)

    if pipeline.inventory_location or pipeline.file_list:
        dockerfile = "./lambda.historic.Dockerfile"
        tag = f"{pipeline.id}-historic"
        build_and_push(dockerfile, tag, pipeline.id)
