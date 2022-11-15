import aws_cdk as cdk
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_lambda_event_sources as lambda_event_sources
import aws_cdk.aws_logs as logs
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as sns_subscriptions
import aws_cdk.aws_sqs as sqs
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

        self.granule_topic = sns.Topic.from_topic_arn(
            self,
            f"{stack_name}_GranuleSNS",
            topic_arn=pipeline.sns,
        )

        self.granule_dlq = sqs.Queue(
            self,
            f"{stack_name}_GranuleDLQ",
            retention_period=cdk.Duration.days(14),
        )

        self.granule_queue = sqs.Queue(
            self,
            "f{stack_name}_GranuleQueue",
            visibility_timeout=cdk.Duration.minutes(15),
            retention_period=cdk.Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=self.granule_dlq,
            ),
        )
        self.sns_subscription = sns_subscriptions.SqsSubscription(
            queue=self.granule_queue,
        )

        self.granule_topic.add_subscription(self.sns_subscription)
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
            memory_size=8000,
            timeout=cdk.Duration.minutes(14),
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        self.granule_function.role.add_to_principal_policy(
            iam.PolicyStatement(
                resources=[
                    "arn:aws:s3:::*",
                ],
                actions=[
                    "s3:Get*",
                    "s3:List*",
                ],
            )
        )

        self.granule_queue.grant_consume_messages(self.granule_function.role)
        self.event_source = lambda_event_sources.SqsEventSource(
            queue=self.granule_queue,
            batch_size=1,
        )
        self.granule_function.add_event_source(self.event_source)
