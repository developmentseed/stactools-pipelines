import yaml
import logging

import docker
from models.pipeline import Pipeline

logging.basicConfig(level=logging.DEBUG)

with open("./pipelines/sentinel1/config.yaml") as f:
    config = yaml.safe_load(f)
    pipeline = Pipeline(**config)

    client = docker.from_env()
    if pipeline.compute == "awslambda":
        dockerfile = "./lambda.Dockerfile"

    image, build_logs = client.images.build(
        path="./",
        dockerfile=dockerfile,
        tag=pipeline.collection,
        buildargs={
            "pipeline": pipeline.id,
        },
    )

    for chunk in build_logs:
        if "stream" in chunk:
            for line in chunk["stream"].splitlines():
                logging.debug(line)
