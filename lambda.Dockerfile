FROM python:3.12 AS builder
ARG pipeline
COPY "./stactools_pipelines/pipelines/${pipeline}/requirements.txt" .
RUN pip install -r requirements.txt --target /tmp/site-packages

FROM public.ecr.aws/lambda/python:3.12
ARG pipeline
COPY "./stactools_pipelines/cognito/*" "./stactools_pipelines/cognito/"
COPY lambda_setup.py ./setup.py
RUN dnf install -y gcc-c++ 
RUN dnf install -y expat expat-devel
RUN pip install .
COPY --from=builder /tmp/site-packages ${LAMBDA_TASK_ROOT}
COPY "./stactools_pipelines/pipelines/${pipeline}/*" "${LAMBDA_TASK_ROOT}/"
RUN dnf remove -y gcc-c++

CMD [ "app.handler" ]
