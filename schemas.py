from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ParkingSlotCreate(BaseModel):
    slot_code: str = Field(..., description="Mã vị trí đỗ, bắt buộc, không trùng")
    zone_name: str = Field(..., description="Tên khu vực, bắt buộc, tối thiểu 3 ký tự")
    max_weight: int = Field(..., description="Tải trọng tối đa (kg), phải > 0")
    is_available: Optional[bool] = True

    @field_validator("slot_code")
    @classmethod
    def slot_code_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("slot_code không được để trống")
        return v.strip()

    @field_validator("zone_name")
    @classmethod
    def zone_name_min_length(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("zone_name không được để trống và phải có độ dài tối thiểu 3 ký tự")
        return v.strip()

    @field_validator("max_weight")
    @classmethod
    def max_weight_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("max_weight phải là số nguyên lớn hơn 0")
        return v


class ParkingSlotResponse(BaseModel):
    id: int
    slot_code: str
    zone_name: str
    max_weight: int
    is_available: bool

    class Config:
        from_attributes = True
