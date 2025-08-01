from pathlib import Path

import aws_cdk as cdk
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_lambda_python_alpha as python
import aws_cdk.aws_logs as logs
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_ssm as ssm
import aws_cdk.aws_sqs as sqs
from constructs import Construct
from aws_cdk.aws_ecr_assets import Platform

from stactools_pipelines.cdk.invoke_function import InvokeFunction
from stactools_pipelines.models.pipeline import Pipeline


class Inventory(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        pipeline: Pipeline,
        granule_queue: sqs.Queue,
        *,
        prefix=None,
    ) -> None:
        super().__init__(scope, id)
        self.stack_name = cdk.Stack.of(self).stack_name

        self.athena_results_bucket = s3.Bucket(
            self,
            f"{self.stack_name}-athena-results",
        )
        self.table_creator_function = python.PythonFunction(
            self,
            id=f"{self.stack_name}-table-creator",
            entry=f"{Path(__file__).parent}/athena_creator",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            memory_size=1000,
            timeout=cdk.Duration.minutes(14),
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                "RESULTS_LOCATION": self.athena_results_bucket.bucket_name,
                "PIPELINE_NAME": pipeline.id,
                "INVENTORY_LOCATION": pipeline.inventory_location,
            },
        )
        self.athena_results_bucket.grant_read_write(self.table_creator_function.role)
        self.table_creator_function.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAthenaFullAccess")
        )
        self.invoke_table_creator = InvokeFunction(
            self,
            id=f"{self.stack_name}-invoke-table-creator",
            function=self.table_creator_function,
        )
        self.process_inventory_chunk = aws_lambda.DockerImageFunction(
            self,
            f"{self.stack_name}-process_chunk",
            code=aws_lambda.DockerImageCode.from_image_asset(
                directory="./",
                platform=Platform.LINUX_AMD64,
                build_args={
                    "pipeline": pipeline.id,
                },
                file="lambda.historic.Dockerfile",
            ),
            memory_size=1000,
            timeout=cdk.Duration.minutes(14),
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                "OUTPUT_LOCATION": f"s3://{self.athena_results_bucket.bucket_name}",
                "DATABASE_NAME": pipeline.id,
                "CHUNK_PARAMETER": (
                    self.chunk_parameter.parameter_name
                    if hasattr(self, "chunk_parameter")
                    else "None"
                ),
                "QUEUE_URL": granule_queue.queue_url,
                "INVENTORY_LOCATION": pipeline.inventory_location,
            },
        )
        granule_queue.grant_send_messages(self.process_inventory_chunk.role)
        self.athena_results_bucket.grant_read_write(self.process_inventory_chunk.role)
        self.process_inventory_chunk.role.add_to_principal_policy(
            iam.PolicyStatement(
                actions=[
                    "athena:StartQueryExecution",
                    "athena:GetQueryExecution",
                    "athena:GetQueryResults",
                    "glue:GetTable",
                    "glue:GetDatabase",
                ],
                resources=["*"],
            )
        )
        ### Open bucket policy needed for inventory location
        self.process_inventory_chunk.role.add_to_principal_policy(
            iam.PolicyStatement(
                resources=[
                    "arn:aws:s3:::*",
                ],
                actions=[
                    "s3:Get*",
                    "s3:List*",
                    "s3:ListBucket",
                ],
            )
        )

        if pipeline.initial_chunk:
            self.chunk_parameter = ssm.StringParameter(
                self,
                f"{self.stack_name}_chunk_parameter",
                string_value=pipeline.initial_chunk,
                parameter_name=f"{self.stack_name}_chunk_parameter",
            )
            self.chunk_parameter.grant_read(self.process_inventory_chunk.role)
            self.chunk_parameter.grant_write(self.process_inventory_chunk.role)

        if pipeline.historic_frequency == 0:
            self.invoke_process_inventory = InvokeFunction(
                self,
                id=f"{self.stack_name}-invoke-process-inventory",
                function=self.process_inventory_chunk,
            ).node.add_dependency(self.invoke_table_creator)
        else:
            self.cron_rule = events.Rule(
                self,
                f"{self.stack_name}-cron-rule",
                schedule=events.Schedule.rate(
                    cdk.Duration.hours(pipeline.historic_frequency)
                ),
            )
            self.cron_rule.add_target(
                events_targets.LambdaFunction(self.process_inventory_chunk)
            )
