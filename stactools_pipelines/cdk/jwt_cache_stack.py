import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
from constructs import Construct


class JwtCacheStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        stack_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, stack_name, **kwargs)

        self.table = dynamodb.Table(
            self,
            id=f"{stack_name}-jwt-cache",
            partition_key=dynamodb.Attribute(
                name="client_id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # On-demand pricing
            time_to_live_attribute="expires_at",  # Attribute to store TTL (epoch seconds)
            removal_policy=cdk.RemovalPolicy.DESTROY,  # For dev/test, change as needed
        )
