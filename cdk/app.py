#!/usr/bin/env python3
import os

import aws_cdk as cdk
from stacks.lambda_stack import LambdaStack

# Required environment variables
stack_name = os.environ["PIPELINE"]

app = cdk.App()

# For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
LambdaStack(
    app,
    stack_name,
)

for k, v in dict(
    Project="aws-asdi",
    Stack=stack_name,
).items():
    cdk.Tags.of(app).add(k, v, apply_to_launched_instances=True)
app.synth()
