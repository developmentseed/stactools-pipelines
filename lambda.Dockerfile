FROM python:3.9 as builder
ARG pipeline
COPY "./aws_asdi_pipelines/pipelines/${pipeline}/requirements.txt" .
RUN pip install -r requirements.txt --target /tmp/site-packages

FROM public.ecr.aws/lambda/python:3.9
ARG pipeline
COPY "./aws_asdi_pipelines/cognito/*" "./aws_asdi_pipelines/cognito/"
COPY setup.py .
RUN pip install .
COPY --from=builder /tmp/site-packages ${LAMBDA_TASK_ROOT}
COPY "./aws_asdi_pipelines/pipelines/${pipeline}/*" "${LAMBDA_TASK_ROOT}/"

CMD [ "app.handler" ]
