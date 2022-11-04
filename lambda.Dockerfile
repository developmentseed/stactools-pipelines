FROM public.ecr.aws/lambda/python:3.9
ARG pipeline

COPY "./pipelines/${pipeline}/app.py" ${LAMBDA_TASK_ROOT}
COPY "./pipelines/${pipeline}/requirements.txt" .

RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
CMD [ "app.handler" ]
