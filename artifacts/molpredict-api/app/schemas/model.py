"""
Esquemas Pydantic para endpoints de información del modelo.
"""
from typing import Any
from pydantic import BaseModel


class ModelInfoResponse(BaseModel):
    name: str
    version: str
    status: str
    task: str
    target: str
    endpoint: str
    trained: bool
    validated: bool
    message: str


class ModelMetricsResponse(BaseModel):
    available: bool
    metrics: Any = None
    message: str


class DatasetCompoundSummary(BaseModel):
    id: str
    name: str
    data_mode: str


class DatasetSummaryResponse(BaseModel):
    total_compounds: int
    compounds: list[DatasetCompoundSummary]
    data_mode: str
    source: str
    generation_date: str
    disclaimer: str
