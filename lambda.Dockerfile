FROM python:3.9 as builder
ARG pipeline
COPY "./stactools_pipelines/pipelines/${pipeline}/requirements.txt" .
RUN pip install -r requirements.txt --target /tmp/site-packages

FROM public.ecr.aws/lambda/python:3.9
ARG pipeline
COPY "./stactools_pipelines/cognito/*" "./stactools_pipelines/cognito/"
COPY lambda_setup.py ./setup.py
RUN pip install .
COPY --from=builder /tmp/site-packages ${LAMBDA_TASK_ROOT}
COPY "./stactools_pipelines/pipelines/${pipeline}/*" "${LAMBDA_TASK_ROOT}/"

CMD [ "app.handler" ]
