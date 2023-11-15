# Stactools-Pipelines
Stactools-Pipelines is a large scale, turnkey processing framework to create STAC metadata and cloud optimized formats for data stored on S3 using [stactools packages](https://github.com/stactools-packages).


![Alt text](/docs/stactools_pipelines_cog.png)


## Requirements
- Python>=3.9
- Docker
- tox
- awscli
- An IAM role with sufficient permissions for creating, destroying and modifying the relevant stack resources.


## Developing Pipelines

A template pipeline structure for Sentinel 1 is included in the repo [here](stactools_pipelines/pipelines/sentinel1).

To develop a new pipeline, create a directory in [pipelines](stactools_pipelines/pipelines) using a simple name for your pipeline dataset.

At a minimum include a
- `requirements.txt` With your application's dependencies.
- `config.yaml` Your pipeline's configuration settings.
- `app.py` A Lambda application with a `handler` function defined which consumes an `SQSEvent` creates a STAC Item and posts it to the `ingestor`.
- `test_app.py` A `pytest` based unit test file which exercises `app.py`.
- `collection.py` A Lambda application with a `handler` function which creates a STAC Collection and posts it to the `ingestor`.
- `test_collection.py` A `pytest` based unit test file which exercises `collection.py`.

### config.yaml structure
- `id` **Required** The pipeline name. This should be the same as the pipeline's parent folder and should use `_`s for separators to support Python module discovery.

- `compute` **Required** Currently only the `awslambda` value is supported.

- `ingestor_url` **Required** The ingestor API's root path with the stage value included.

- `secret_arn` **Required** The secret manager ARN for using a Cognito JWKS implementation with the ingestor API.

- `sns` **Optional** The SNS topic to listen to for new granule notifications.

- `inventory_location` **Optional** The location of an S3 inventory that can be used by the `pipeline` to process and ingest existing granules.  Include a `historic.py` file (and a `test_historic.py`) in your pipeline which implements a `query_inventory`, `row_to_message_body` and `handler` method to query the inventory and send the results to the processing queue. If provided, an athena table is created. Default is `None`. If provided, `file_list` can't be provided. 

- `historic_frequency` **Optional** If an `inventory_location` is included the `historic_frequency` (how often in hours the `historic.py` is run) must also be included.  A value of `0` indicates that the `historic.py` function will run a single time on deployment and process the entire inventory. If a value of > `0` is specified then an `initial_chunk` must also be specified.  The pipeline will build a stack which uses these values to incrementally chunk through the inventory file with `cron` executions to process until the entire inventory has been processed.

- `file_list` **Optional** Location of a non-standard AWS inventory file. Default is `None`. If provided, no Athena table is created and the 'historic' lambda processes that list. If provided, `inventory_location` can't be provided. 

### Testing a Pipeline
Create an environment setting using your pipline name.
```
$ export PIPELINE=<Your pipeline name>
```

To run your pipeline unit tests
```
$ tox
```

### Deploying a Pipeline
Deploying a pipeline will use the pipeline's config.yaml to deploy all the necessary resources for running the pipeline.  Including STAC Collection and Item creation Lambdas and any queues or Athena tables that are required. If an `sns` was specified it will begin processing notifications as soon as deployment is complete .

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

Deploy the infrastructure for your pipeline with
```
$ cdk deploy
```

## Developing stactools-pipelines
To create a development virtual environment for core repository development use
```
$ tox -e dev
$ source devenv/bin/activate
```
