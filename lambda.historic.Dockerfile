FROM public.ecr.aws/lambda/python:3.9
ARG pipeline
COPY "./aws_asdi_pipelines/historic/*" "./aws_asdi_pipelines/historic/"
COPY setup.py .
RUN pip install .
COPY "./aws_asdi_pipelines/pipelines/${pipeline}/historic.py" "${LAMBDA_TASK_ROOT}/app.py"

CMD [ "app.handler" ]
