from enum import Enum
from typing import Optional
from typing_extensions import Self

from pydantic import BaseModel, model_validator


class ComputeEnum(str, Enum):
    awslambda = "awslambda"


class Pipeline(BaseModel):
    id: str
    compute: ComputeEnum
    secret_arn: str
    ingestor_url: str
    sns: Optional[str]
    inventory_location: Optional[str] = None
    historic_frequency: Optional[int] = None
    initial_chunk: Optional[str] = None

    @model_validator(mode="after")
    def historic_frequency_if_inventory_location(self) -> Self:
        if self.inventory_location and self.historic_frequency is None:
            raise ValueError("Must include historic_frequency with inventory_location")
        return self

    @model_validator(mode="after")
    def initial_chunk_if_historic_frequency_greater_than_0(self) -> Self:
        if self.historic_frequency:
            if self.historic_frequency > 0 and self.initial_chunk is None:
                raise ValueError(
                    "Must include initial_chunk when historic_frequency > 0"
                )
        return self
