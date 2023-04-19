import aws_cdk as cdk
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_lambda_event_sources as lambda_event_sources
import aws_cdk.aws_sqs as sqs
from constructs import Construct


class Queue(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        function: aws_lambda.DockerImageFunction,
        *,
        prefix=None,
    ) -> None:
        super().__init__(scope, id)
        self.stack_name = cdk.Stack.of(self).stack_name
        self.granule_dlq = sqs.Queue(
            self,
            f"{self.stack_name}_GranuleDLQ",
            retention_period=cdk.Duration.days(14),
        )
        self.granule_queue = sqs.Queue(
            self,
            f"{self.stack_name}_GranuleQueue",
            visibility_timeout=cdk.Duration.minutes(15),
            retention_period=cdk.Duration.days(14),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=self.granule_dlq,
            ),
        )
        self.granule_queue.grant_consume_messages(function.role)
        self.event_source = lambda_event_sources.SqsEventSource(
            queue=self.granule_queue,
            batch_size=1,
        )
        function.add_event_source(self.event_source)
