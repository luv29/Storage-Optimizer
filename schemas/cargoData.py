from pydantic import BaseModel, Field
from typing import Literal, List

class CargoData(BaseModel):
    Cargo_ID: str = Field(..., example="C00001")
    Size_Category: Literal["Small", "Medium", "Large", "Oversized"]
    Weight: float = Field(..., gt=0, example=50.0)
    Hazardous: int = Field(..., example=0)
    Stackable: int = Field(..., example=1)
    Duration: int = Field(..., gt=0, example=2)
    Transport_Type: Literal["Manual", "Forklift"]
    
    # 10x10 Matrix for slot availability
    Slot_Matrix: List[List[int]] = Field(..., example=[
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
        [0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
        [1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
        [0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    ])
