from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PlacementInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gender: Literal["M", "F"]
    ssc_p: float = Field(ge=0, le=100)
    ssc_b: Literal["Central", "Others"]
    hsc_p: float = Field(ge=0, le=100)
    hsc_b: Literal["Central", "Others"]
    hsc_s: Literal["Commerce", "Science", "Arts"]
    degree_p: float = Field(ge=0, le=100)
    degree_t: Literal["Sci&Tech", "Comm&Mgmt", "Others"]
    workex: Literal["Yes", "No"]
    etest_p: float = Field(ge=0, le=100)
    specialisation: Literal["Mkt&HR", "Mkt&Fin"]
    mba_p: float = Field(ge=0, le=100)


class PredictionResponse(BaseModel):
    prediction: int
    predicted_status: Literal["Placed", "Not Placed"]
    placement_probability: float


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    status: str
    message: str
    details: list[ErrorDetail]


class BatchPredictionRequest(BaseModel):
    customers: list[PlacementInput] = Field(min_length=1)


class BatchPredictionResponse(BaseModel):
    count: int
    predictions: list[PredictionResponse]
