FROM python:3.9 as builder
ARG pipeline
COPY "./aws_asdi_pipelines/pipelines/${pipeline}/requirements.txt" .
RUN pip install -r requirements.txt --target /tmp/site-packages

FROM public.ecr.aws/lambda/python:3.9
ARG pipeline
COPY --from=builder /tmp/site-packages ${LAMBDA_TASK_ROOT}
COPY "./aws_asdi_pipelines/pipelines/${pipeline}/app.py" ${LAMBDA_TASK_ROOT}

CMD [ "app.handler" ]
