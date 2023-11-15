import aws_cdk as cdk
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as sns_subscriptions
from constructs import Construct

from stactools_pipelines.cdk.inventory import Inventory
from stactools_pipelines.cdk.invoke_function import InvokeFunction
from stactools_pipelines.cdk.pipeline_function import PipelineFunction
from stactools_pipelines.cdk.queue import Queue
from stactools_pipelines.models.pipeline import Pipeline


class LambdaStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        stack_name: str,
        pipeline: Pipeline,
        **kwargs,
    ) -> None:
        super().__init__(scope, stack_name)
        self.collection_function = PipelineFunction(
            self,
            id=f"{stack_name}-collection_function",
            pipeline=pipeline,
            collection=True,
        )
        self.invoke_collection_function = InvokeFunction(
            self,
            id=f"{stack_name}-invoke-collection_function",
            function=self.collection_function.function,
        )

        self.granule_function = PipelineFunction(
            self,
            id=f"{stack_name}-granule_function",
            pipeline=pipeline,
        )

        if pipeline.sns or pipeline.inventory_location or pipeline.file_list:
            self.queue = Queue(
                self,
                id=f"{stack_name}-queue",
                function=self.granule_function.function,
            )
        else:
            self.invoke_granule_function = InvokeFunction(
                self,
                id=f"{stack_name}-invoke-granule_function",
                function=self.granule_function.function,
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

        if pipeline.inventory_location or pipeline.file_list:
            self.inventory = Inventory(
                self,
                id=f"{stack_name}-inventory",
                pipeline=pipeline,
                granule_queue=self.queue.granule_queue,
            )
