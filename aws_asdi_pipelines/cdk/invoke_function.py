import aws_cdk as cdk
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.custom_resources as custom_resources
from constructs import Construct


class InvokeFunction(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        function: aws_lambda.Function,
        *,
        prefix=None,
    ) -> None:
        super().__init__(scope, id)
        self.invoke_lambda = custom_resources.AwsCustomResource(
            scope=self,
            id="invoke_lambda",
            policy=(
                custom_resources.AwsCustomResourcePolicy.from_statements(
                    statements=[
                        iam.PolicyStatement(
                            actions=["lambda:InvokeFunction"],
                            effect=iam.Effect.ALLOW,
                            resources=[function.function_arn],
                        )
                    ]
                )
            ),
            timeout=cdk.Duration.minutes(15),
            on_create=custom_resources.AwsSdkCall(
                service="Lambda",
                action="invoke",
                parameters={
                    "FunctionName": function.function_name,
                    "InvocationType": "Event",
                },
                physical_resource_id=custom_resources.PhysicalResourceId.of(
                    "JobSenderTriggerPhysicalId"
                ),
            ),
        )
