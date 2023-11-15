from enum import Enum
from typing import Optional

from pydantic import BaseModel, model_validator


class ComputeEnum(str, Enum):
    awslambda = "awslambda"


class Pipeline(BaseModel):
    id: str
    compute: ComputeEnum
    secret_arn: str
    ingestor_url: str
    sns: Optional[str] = None
    inventory_location: Optional[str] = None
    historic_frequency: Optional[int] = None
    initial_chunk: Optional[str] = None
    file_list: Optional[str] = None

    @model_validator(mode="after")
    def historic_frequency_if_inventory_location(cls, values):
        if values.inventory_location and values.historic_frequency is None:
            raise ValueError("Must include historic_frequency with inventory_location")
        return values

    @model_validator(mode="after")
    def initial_chunk_if_historic_frequency_greater_than_0(cls, values):
        if values.historic_frequency:
            if values.historic_frequency > 0 and values.initial_chunk is None:
                raise ValueError(
                    "Must include initial_chunk when historic_frequency > 0"
                )
        return values

    @model_validator(mode="after")
    def file_list_or_inventory_location(cls, values):
        assert not (
            values.file_list is not None and values.inventory_location is not None
        ), "Must include either inventory_location or file_list but not both"
        return values
