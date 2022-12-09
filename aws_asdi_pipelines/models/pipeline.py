from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ComputeEnum(str, Enum):
    awslambda = "awslambda"
    awsbatch = "awsbatch"


class Pipeline(BaseModel):
    id: str
    arco: bool
    collection: str
    compute: ComputeEnum
    sns: str
    secret_arn: str
    ingestor_url: str
    inventory_location: Optional[str]
    initial_chunk: Optional[str]
