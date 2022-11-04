from enum import Enum
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
