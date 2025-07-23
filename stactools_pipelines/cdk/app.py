import os

import aws_cdk as cdk
import yaml

from stactools_pipelines.cdk.jwt_cache_stack import JwtCacheStack
from stactools_pipelines.cdk.lambda_stack import LambdaStack
from stactools_pipelines.models.pipeline import Pipeline

# Required environment variables
pipeline = os.environ["PIPELINE"]
stack_name = pipeline.replace("_", "-")

app = cdk.App()

jwt_cache_stack = JwtCacheStack(
    app,
    stack_name,
)

with open(f"./stactools_pipelines/pipelines/{pipeline}/config.yaml") as f:
    config = yaml.safe_load(f)
    pipeline = Pipeline(**config)

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    LambdaStack(
        app,
        stack_name,
        pipeline,
        jwt_cache_table=jwt_cache_stack.table,
    )

    for k, v in dict(
        Project="aws-asdi", Stack=stack_name, Pipeline=pipeline.id
    ).items():
        cdk.Tags.of(app).add(k, v, apply_to_launched_instances=True)
    app.synth()
