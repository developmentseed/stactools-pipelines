from pydantic_settings import BaseSettings


class Deployment(BaseSettings):
    project: str
    stage: str
    pipeline: str
