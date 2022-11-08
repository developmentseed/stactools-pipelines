import os

import aws_cdk as cdk
import yaml

from aws_asdi_pipelines.cdk.lambda_stack import LambdaStack
from aws_asdi_pipelines.models.pipeline import Pipeline

# Required environment variables
stack_name = os.environ["PIPELINE"]

with open(f"./aws_asdi_pipelines/pipelines/{stack_name}/config.yaml") as f:
    config = yaml.safe_load(f)
    pipeline = Pipeline(**config)

    app = cdk.App()

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    LambdaStack(
        app,
        stack_name,
        pipeline,
    )

    for k, v in dict(
        Project="aws-asdi", Stack=stack_name, Pipeline=pipeline.id
    ).items():
        cdk.Tags.of(app).add(k, v, apply_to_launched_instances=True)
    app.synth()
