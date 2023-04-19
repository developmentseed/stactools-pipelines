import aws_cdk as cdk
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_logs as logs
import aws_cdk.aws_secretsmanager as secretsmanager
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as sns_subscriptions
from constructs import Construct

from aws_asdi_pipelines.cdk.inventory import Inventory
from aws_asdi_pipelines.cdk.invoke_function import InvokeFunction
from aws_asdi_pipelines.cdk.queue import Queue
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
        self.secret = secretsmanager.Secret.from_secret_complete_arn(
            self, f"{pipeline.id}_secret_new", secret_complete_arn=pipeline.secret_arn
        )
        self.repo = ecr.Repository.from_repository_name(
            self,
            f"{stack_name}_Repository",
            repository_name=pipeline.id,
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

        if pipeline.sns or pipeline.inventory_location:
            self.queue = Queue(
                self,
                "f{stack_name}-queue",
                function=self.granule_function,
            )
        else:
            self.invoke_granule_function = InvokeFunction(
                self,
                id=f"{stack_name}-invoke-granule_function",
                function=self.granule_function,
            )

        if pipeline.sns:
            self.granule_topic = sns.Topic.from_topic_arn(
                self,
                f"{stack_name}-granule-sns",
                topic_arn=pipeline.sns,
            )
            self.sns_subscription = sns_subscriptions.SqsSubscription(
                queue=self.queue.granule_queue,
            )
            self.granule_topic.add_subscription(self.sns_subscription)

        if pipeline.inventory_location:
            self.inventory = Inventory(
                self,
                id=f"{stack_name}-inventory",
                pipeline=pipeline,
                granule_queue=self.queue.granule_queue,
            )
