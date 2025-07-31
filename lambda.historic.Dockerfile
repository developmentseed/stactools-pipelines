FROM public.ecr.aws/lambda/python:3.12
ARG pipeline
COPY "./stactools_pipelines/historic/*" "./stactools_pipelines/historic/"
COPY setup.py .
RUN pip install .
COPY "./stactools_pipelines/pipelines/${pipeline}/historic.py" "${LAMBDA_TASK_ROOT}/app.py"

CMD [ "app.handler" ]
