from dataclasses import dataclass
from pydantic import BaseModel, Field


class MarketInput(BaseModel):
    symbol_name: str
    high: float
    low: float
    volume: float
    month: str
    year: str


class MarketResponse(BaseModel):
    high: str = Field(coerce_numbers_to_str=True)
    low: str = Field(coerce_numbers_to_str=True)
    volume: str = Field(coerce_numbers_to_str=True)


class SymbolInput(BaseModel):
    symbol_name: str


@dataclass
class Market:
    high: float
    low: float
    volume: float
    month: str
    year: str
    symbol_id: int


@dataclass
class Symbols:
    id: int
    symbol_name: str


