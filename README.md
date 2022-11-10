# AWS-ASDI-Pipelines

![Alt text](/docs/aws_asdi_cog.png)


## Requirements
- Python>=3.9
- Docker
- tox
- aws-cli
- An IAM role with sufficient permissions for creating, destroying and modifying the relevant stack resources.


## Developing Pipelines

A template pipeline structure for Sentinel 1 is included in the repo [here](aws_asdi_pipelines/pipelines/sentinel1).

To develop a new pipeline, create a directory in [pipelines](aws_asdi_pipelines/pipelines) using a simple name for your pipeline dataset.

At a minimum include a
- `requirements.txt` With your application's dependencies.
- `config.yaml` Your pipeline's configuration settings.
- `app.py` A Lambda application with a `handler` function defined which consumes an `SQSEvent`.
- `test_app.py` A `pytest` based unit test file which exercises your application.

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
Create a development virtual environment with
```
$ tox -e dev
$ source devenv/bin/activate
```
Create environment settigns for your pipeline deployment
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

## Developing aws-asdi-pipelines
To create a development virtual environment for core repository development use
```
$ tox -e dev
$ source devenv/bin/activate
```
