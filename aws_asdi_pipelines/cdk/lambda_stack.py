import aws_cdk as cdk
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as events_targets
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_lambda_event_sources as lambda_event_sources
import aws_cdk.aws_logs as logs
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_secretsmanager as secretsmanager
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as sns_subscriptions
import aws_cdk.aws_sqs as sqs
import aws_cdk.aws_ssm as ssm
import aws_cdk.custom_resources as custom_resources
from constructs import Construct

from aws_asdi_pipelines.models.pipeline import Pipeline


class LambdaStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        stack_name: str,
        pipeline: Pipeline,
        **kwargs,
    ) -> None:
        super().__init__(scope, stack_name)
        self.granule_dlq = sqs.Queue(
            self,
            f"{stack_name}_GranuleDLQ",
            retention_period=cdk.Duration.days(14),
        )

        self.granule_queue = sqs.Queue(
            self,
            f"{stack_name}_GranuleQueue",
            visibility_timeout=cdk.Duration.minutes(15),
            retention_period=cdk.Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=self.granule_dlq,
            ),
        )
        if pipeline.sns:
            self.granule_topic = sns.Topic.from_topic_arn(
                self,
                f"{stack_name}_GranuleSNS",
                topic_arn=pipeline.sns,
            )
            self.sns_subscription = sns_subscriptions.SqsSubscription(
                queue=self.granule_queue,
            )
            self.granule_topic.add_subscription(self.sns_subscription)

        self.secret = secretsmanager.Secret.from_secret_complete_arn(
            self, f"{stack_name}_secret_new", secret_complete_arn=pipeline.secret_arn
        )
        self.repo = ecr.Repository.from_repository_name(
            self,
            f"{stack_name}_Repository",
            repository_name=stack_name,
        )

        self.granule_function = aws_lambda.DockerImageFunction(
            self,
            f"{stack_name}-granule_function",
            code=aws_lambda.DockerImageCode.from_ecr(
                repository=self.repo, tag="latest"
            ),
            memory_size=1000,
            timeout=cdk.Duration.minutes(14),
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                "CLIENT_SECRET": self.secret.secret_value_from_json(
                    "client_secret"
                ).to_string(),
                "CLIENT_ID": self.secret.secret_value_from_json(
                    "client_id"
                ).to_string(),
                "DOMAIN": self.secret.secret_value_from_json(
                    "cognito_domain"
                ).to_string(),
                "SCOPE": self.secret.secret_value_from_json("scope").to_string(),
                "INGESTOR_URL": pipeline.ingestor_url,
            },
        )

        self.open_buckets_statement = iam.PolicyStatement(
            resources=[
                "arn:aws:s3:::*",
            ],
            actions=[
                "s3:Get*",
                "s3:List*",
                "s3:ListBucket",
            ],
        )

        self.granule_function.role.add_to_principal_policy(self.open_buckets_statement)

        self.granule_queue.grant_consume_messages(self.granule_function.role)
        self.event_source = lambda_event_sources.SqsEventSource(
            queue=self.granule_queue,
            batch_size=1,
        )
        self.granule_function.add_event_source(self.event_source)

        if pipeline.inventory_location:
            self.athena_results_bucket = s3.Bucket(
                self,
                f"{stack_name}-athena-results",
            )
            cdk.CfnOutput(
                self,
                "AthenaResultsBucket",
                value=self.athena_results_bucket.bucket_name,
            )
            if pipeline.initial_chunk:
                self.chunk_parameter = ssm.StringParameter(
                    self,
                    f"{stack_name}_chunk_parameter",
                    string_value=pipeline.initial_chunk,
                    parameter_name=f"{stack_name}_chunk_parameter",
                )
            self.repo_historic = ecr.Repository.from_repository_name(
                self,
                f"{stack_name}_repository_historic",
                repository_name=f"{stack_name}-historic",
            )

            self.process_inventory_chunk = aws_lambda.DockerImageFunction(
                self,
                f"{stack_name}-process_chunk",
                code=aws_lambda.DockerImageCode.from_ecr(
                    repository=self.repo_historic, tag="latest"
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
                    "QUEUE_URL": self.granule_queue.queue_url,
                    "INVENTORY_LOCATION": pipeline.inventory_location,
                },
            )

            if pipeline.historic_frequency == 0:
                custom_resources.AwsCustomResource(
                    scope=self,
                    id="invoke_lambda",
                    policy=(
                        custom_resources.AwsCustomResourcePolicy.from_statements(
                            statements=[
                                iam.PolicyStatement(
                                    actions=["lambda:InvokeFunction"],
                                    effect=iam.Effect.ALLOW,
                                    resources=[
                                        self.process_inventory_chunk.function_arn
                                    ],
                                )
                            ]
                        )
                    ),
                    timeout=cdk.Duration.minutes(15),
                    on_create=custom_resources.AwsSdkCall(
                        service="Lambda",
                        action="invoke",
                        parameters={
                            "FunctionName": self.process_inventory_chunk.function_name,
                            "InvocationType": "Event",
                        },
                        physical_resource_id=custom_resources.PhysicalResourceId.of(
                            "JobSenderTriggerPhysicalId"
                        ),
                    ),
                )
            else:
                self.cron_rule = events.Rule(
                    self,
                    f"{stack_name}_cron_rule",
                    schedule=events.Schedule.rate(
                        cdk.Duration.hours(pipeline.historic_frequency)
                    ),
                )
                self.cron_rule.add_target(
                    events_targets.LambdaFunction(self.process_inventory_chunk)
                )
            self.process_inventory_chunk.role.add_to_principal_policy(
                self.open_buckets_statement
            )
            self.granule_queue.grant_send_messages(self.process_inventory_chunk.role)
            if pipeline.initial_chunk:
                self.chunk_parameter.grant_read(self.process_inventory_chunk.role)
                self.chunk_parameter.grant_write(self.process_inventory_chunk.role)

            self.process_inventory_chunk.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "athena:StartQueryExecution",
                        "athena:GetQueryExecution",
                        "athena:GetQueryResults",
                        "glue:GetTable",
                    ],
                    resources=["*"],
                )
            )
            self.process_inventory_chunk.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:AbortMultipartUpload",
                        "s3:PutObject",
                        "s3:ListMultipartUploadParts",
                    ],
                    resources=[
                        self.athena_results_bucket.bucket_arn,
                        f"{self.athena_results_bucket.bucket_arn}/*",
                    ],
                )
            )
