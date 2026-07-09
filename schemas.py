from pydantic import BaseModel, Field
from typing import Optional


class ParkingSlotCreate(BaseModel):
    slot_code: str = Field(..., min_length=1, max_length=50)
    zone_name: str = Field(..., min_length=3, max_length=255)
    max_weight: int = Field(..., gt=0)  # bắt buộc > 0
    is_available: Optional[bool] = True