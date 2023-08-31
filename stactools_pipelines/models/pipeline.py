from enum import Enum
from typing import Optional

from pydantic import BaseModel, root_validator


class ComputeEnum(str, Enum):
    awslambda = "awslambda"


class Pipeline(BaseModel):
    id: str
    compute: ComputeEnum
    secret_arn: str
    ingestor_url: str
    sns: Optional[str]
    inventory_location: Optional[str]
    historic_frequency: Optional[int]
    initial_chunk: Optional[str]
    athena_table: Optional[bool] = True

    @root_validator(pre=False)
    def historic_frequency_if_inventory_location(cls, values):
        if values["inventory_location"] and values["historic_frequency"] is None:
            raise ValueError("Must include historic_frequency with inventory_location")
        return values

    @root_validator(pre=False)
    def initial_chunk_if_historic_frequency_greater_than_0(cls, values):
        if values["historic_frequency"]:
            if values["historic_frequency"] > 0 and values["initial_chunk"] is None:
                raise ValueError(
                    "Must include initial_chunk when historic_frequency > 0"
                )
        return values

    @root_validator(pre=False)
    def no_athena_table_if_no_inventory_location(cls, values):
        if values["athena_table"] and values["inventory_location"] is None:
            raise ValueError(
                "Must include an inventory location to create athena resources"
            )
        return values
