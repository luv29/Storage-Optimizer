from pydantic import BaseModel
from typing import Literal

class CargoInfo(BaseModel):
    cargo_id: str
    expected_arrival_time: str  
    transport_type: Literal["manual", "forklift"]
