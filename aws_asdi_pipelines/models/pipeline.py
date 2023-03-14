from enum import Enum
from typing import Optional

from pydantic import BaseModel, root_validator


class ComputeEnum(str, Enum):
    awslambda = "awslambda"
    awsbatch = "awsbatch"


class Pipeline(BaseModel):
    id: str
    compute: ComputeEnum
    secret_arn: str
    ingestor_url: str
    queue: bool
    sns: Optional[str]
    inventory_location: Optional[str]
    initial_chunk: Optional[str]
    historic_frequency: Optional[int]

    @root_validator(pre=False)
    def historic_frequency_if_inventory_location(cls, values):
        if values["inventory_location"] and values["historic_frequency"] is None:
            raise ValueError("Must include historic_frequency with inventory_location")
        return values
