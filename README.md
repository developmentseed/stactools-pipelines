# Stactools-Pipelines
Stactools-Pipelines is a large scale, turnkey processing framework to create STAC metadata and cloud optimized formats for data stored on S3 using [stactools packages](https://github.com/stactools-packages). It's goal is to make it easier for teams to develop scalable metadata pipelines by reducing the infrastructure boilerplate they need to build themselves.


![Alt text](/docs/aws_asdi_cog.png)


## Requirements
- Python>=3.11
- Docker
- tox
- awscli
- An IAM role with sufficient permissions for creating, destroying and modifying the relevant stack resources.


## Stactools packages
This framework expects that a [stactools package](https://github.com/stactools-packages) has already been created for your dataset of interest and that the dataset is stored on S3.  Check out [stactools-packages](https://stactools-packages.github.io/) to find out if a package already exists or how to create your own.

## Developing Pipelines
This is a template repository.  You can follow [these instructions](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) to create your organization's own repo from the template. Once you have created your own repository from the template, you develop your own pipelines.

To install for pipeline development run
```
pip install .["dev"]
```

An example pipeline structure for Sentinel 1 is included in the repo [here](stactools_pipelines/pipelines/sentinel1) to use as a reference for developing your own pipeline.

To develop a new pipeline create a directory in [pipelines](stactools_pipelines/pipelines) using a simple name for your pipeline dataset.


At a minimum you need to include

- `app.py` A Lambda application with a `handler` function defined which consumes an `SQSEvent` creates a STAC Item and posts it to the `ingestor`.

- `requirements.txt` That contains the `app.py`'s dependencies so a container image can be built.

- `config.yaml` Your pipeline's configuration settings.

- `test_app.py` A `pytest` based unit test file which exercises `app.py`.

- `collection.py` A Lambda application with a `handler` function which creates a STAC Collection and posts it to the `ingestor`.

- `test_collection.py` A `pytest` based unit test file which exercises `collection.py`.

If you have pre-existing granules in your bucket and your bucket has [S3 Inventory](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-inventory.html) enabled, you can also optionally include functions which read the inventory to process these pre-existing granules.  These include

- `historic.py` A Lambda application which queries rows from the bucket's inventory file loaded into an Athena table.

- `test_historic.py` A `pytest` based unit test file which exercises `historic.py`.

### config.yaml structure
- `id` **Required** The pipeline name. This should be the same as the pipeline's parent folder and should use `_`s for separators to support Python module discovery.

- `compute` **Required** Currently only the `awslambda` value is supported.

- `ingestor_url` **Required** The ingestor API's root path with the stage value included.

- `secret_arn` **Required** The secret manager ARN for using a Cognito JWKS implementation with the ingestor API.

- `sns` **Optional** The SNS topic to listen to for new granule notifications.

- `inventory_location` **Optional** The location of an S3 inventory or file listing that can be used by the `pipeline` to process and ingest existing granules.  Include a `historic.py` file (and a `test_historic.py`) in your pipeline which implements a `query_inventory`, `row_to_message_body` and `handler` method to query the inventory and send the results to the processing queue.

- `historic_frequency` **Optional** If an `inventory_location` is included the `historic_frequency` (how often in hours the `historic.py` is run) must also be included.  A value of `0` indicates that the `historic.py` function will run a single time on deployment and process the entire inventory. If a value of > `0` is specified then an `initial_chunk` must also be specified.  The pipeline will build a stack which uses these values to incrementally chunk through the inventory file with `cron` executions to process until the entire inventory has been processed.

### Writing your pipeline's app.py
Your pipeline's `app.py` function receives notification messages about granules to be processed and uses the information in these messages to create new STAC items (and optionally, new cloud optimized versions of the data). You'll need to understand a bit about the strcture of the files that make up a granule in your dataset and a bit about how the SNS notifications are configured for your bucket (if they are enabled).

As an example, note that the SNS topic for the Sentinel-1 bucket uses a [custom message structure](https://github.com/developmentseed/stactools-pipelines/blob/main/stactools_pipelines/pipelines/sentinel1/test_app.py#L14-L17) that includes an `id` and `path` property describing the "directory" key rather than individual file keys like most SNS configurations.  Note that the Sentinel-1 [app.py](https://github.com/developmentseed/stactools-pipelines/blob/main/stactools_pipelines/pipelines/sentinel1/app.py#L23) has logic to correctly parse this message and that the Sentinel-1 stactools package actually expects an `href` value that is a "directory" rather than a file.

At a minimum the `handler` method in your pipeline's `app.py` should create a STAC item and post that item to the ingestor endpoint.

### Unit testing your pipeline's app.py
To make unit testing easier and more consistent, `stactools-pipelines` includes a number of pytest fixtures and mocks which you can use to isolate your handler function from external services and verify that it behaving as expected.  These fixtures use some [pytest parameterization](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html) magic to patch the appropriate imports in your pipeline's `app.py` when your tests are run.

Using the Sentinel-1 pipeline as an example.  The `test_handler` [is decorated with[(https://docs.pytest.org/en/7.1.x/how-to/parametrize.html) the `pipeline_id` and `module`.  When the test is run all the fixtures included in [conftest.py](https://github.com/developmentseed/stactools-pipelines/blob/main/stactools_pipelines/pipelines/conftest.py) patch your `app.py`'s use of the real module allowing you to test in isolation.  It is recommended to use these fixtures for unit testing and behavior verification.

To run the unit tests for your pipeline

Create an environment setting using your pipline name.
```
$ export PIPELINE=<Your pipeline name>
```

And call tox to run your unit tests
```
$ tox
```

## Deploying a Pipeline
Deploying a pipeline will use the pipeline's `config.yaml` to deploy all the necessary infrastructure.  This includes STAC Collection and Item creation Lambdas and any queues or Athena tables that are required. A new completely separate Cloudformation stack is created for each pipeline.  The pipleine being deployed is controlled by the `PIPELINE` environment variable.  The `collection.py` Lambda is executed automatically by the stack after deployment in order to create the STAC collection in the target STAC API.  If an `sns` was specified in the `config.yaml` the `app.py` Lambda will be subscribed and will begin processing notifications as soon as the stack deployment is complete.

To deploy a pipeline

Create a development virtual environment with
```
$ tox -e dev
$ source devenv/bin/activate
```
Create environment settings for your pipeline deployment
```
$ export PROJECT=<The project name for resource cost tracking>
$ export PIPELINE=<Your pipeline name>
```
With an AWS profile enabled with sufficient permissions build and push your pipeline image with
```
$ python image_builder.py
```
This will package your pipeline's Lambda code and the its dependencies specified in the requirements.txt into a Docker image and push it to ECR for use by the pipeline Lambdas.


Deploy the infrastructure for your pipeline with
```
$ cdk deploy
```
This will create Cloudformation stack for your pipline.


## Developing stactools-pipelines
To create a development virtual environment for core repository development use
```
$ tox -e dev
$ source devenv/bin/activate
```
