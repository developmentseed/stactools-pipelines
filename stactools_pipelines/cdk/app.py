import aws_cdk as cdk
import yaml

from stactools_pipelines.cdk.lambda_stack import LambdaStack
from stactools_pipelines.models.deployment import Deployment
from stactools_pipelines.models.pipeline import Pipeline

deployment = Deployment()

with open(f"./stactools_pipelines/pipelines/{deployment.pipeline}/config.yaml") as f:
    config = yaml.safe_load(f)
    pipeline = Pipeline(**config)

    app = cdk.App()

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    LambdaStack(
        app,
        deployment.stack_name,
        pipeline,
    )

    for k, v in dict(
        Project=deployment.project,
        Stack=deployment.stack_name,
        Pipeline=pipeline.id,
        Stage=deployment.stage,
    ).items():
        cdk.Tags.of(app).add(k, v, apply_to_launched_instances=True)
    app.synth()
