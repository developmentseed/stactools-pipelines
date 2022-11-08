import aws_cdk as cdk
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as sns_subscriptions
import aws_cdk.aws_sqs as sqs
from constructs import Construct

from ..models.pipeline import Pipeline


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
            topic_arn="wat",
        )

        self.granule_dlq = sqs.Queue(
            self,
            f"{stack_name}_GranuleDLQ",
            retention_period=cdk.Duration.days(14),
        )

        self.granule_queue = sqs.Queue(
            self,
            "f{stack_name}_GranuleQueue",
            visibility_timeout=cdk.Duration.hours(12),
            retention_period=cdk.Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=self.granule_dlq,
            ),
        )

        self.sns_subscription = sns_subscriptions.SqsSubscription(
            queue=self.granule_queue,
            dead_letter_queue=self.granule_dlq,
        )

        self.granule_topic.add_subscription(self.sns_subscription)
