import os

import aws_cdk as cdk
import yaml

from stactools_pipelines.cdk.lambda_stack import LambdaStack
from stactools_pipelines.models.pipeline import Pipeline

# Required environment variables
pipeline = os.environ["PIPELINE"]
project = os.environ["PROJECT"]
stack_name = pipeline.replace("_", "-")

with open(f"./stactools_pipelines/pipelines/{pipeline}/config.yaml") as f:
    config = yaml.safe_load(f)
    pipeline = Pipeline(**config)

    app = cdk.App()

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    LambdaStack(
        app,
        stack_name,
        pipeline,
    )

    for k, v in dict(Project=project, Stack=stack_name, Pipeline=pipeline.id).items():
        cdk.Tags.of(app).add(k, v, apply_to_launched_instances=True)
    app.synth()
