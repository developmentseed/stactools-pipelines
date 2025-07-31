import aws_cdk as cdk
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as aws_lambda
import aws_cdk.aws_logs as logs
import aws_cdk.aws_secretsmanager as secretsmanager
from constructs import Construct
from aws_cdk.aws_ecr_assets import Platform

from stactools_pipelines.models.pipeline import Pipeline


class PipelineFunction(Construct):

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        pipeline: Pipeline,
        collection: bool = False,
        jwt_cache_table: dynamodb.Table,
        prefix=None,
    ) -> None:
        super().__init__(scope, id)
        self.stack_name = cdk.Stack.of(self).stack_name
        if collection:
            dockerfile = "lambda.collection.Dockerfile"
            function_name = f"{self.stack_name}-collection_function"
        else:
            dockerfile = "lambda.Dockerfile"
            function_name = f"{self.stack_name}-granule_function"

        self.secret = secretsmanager.Secret.from_secret_complete_arn(
            self, f"{pipeline.id}_secret_new", secret_complete_arn=pipeline.secret_arn
        )

        self.function = aws_lambda.DockerImageFunction(
            self,
            function_name,
            code=aws_lambda.DockerImageCode.from_image_asset(
                directory="./",
                platform=Platform.LINUX_AMD64,
                build_args={
                    "pipeline": pipeline.id,
                },
                file=dockerfile,
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
                "JWT_CACHE_TABLE_NAME": jwt_cache_table.table_name,
            },
        ) 
        jwt_cache_table.grant_read_write_data(self.function)

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
        self.function.role.add_to_principal_policy(self.open_buckets_statement)
