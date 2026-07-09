from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import Base, engine, get_db
from models import ParkingSlot
from schemas import ParkingSlotCreate, ParkingSlotResponse
from utils import json_response

# Tạo bảng nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Quản lý Vị trí Xe Công nghệ tại Bãi đỗ")


# ----------------------------------------------------------------------------
# EXCEPTION HANDLERS - đảm bảo mọi response (kể cả lỗi) đều theo cấu trúc chuẩn
# ----------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    message = errors[0]["msg"] if errors else "Dữ liệu không hợp lệ"
    return json_response(
        status_code=422,
        message=message,
        error="Unprocessable Entity",
        data=None,
        path=str(request.url.path),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return json_response(
        status_code=exc.status_code,
        message=exc.detail,
        error=exc.detail,
        data=None,
        path=str(request.url.path),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return json_response(
        status_code=500,
        message="Lỗi hệ thống, vui lòng thử lại sau",
        error=str(exc),
        data=None,
        path=str(request.url.path),
    )


# ----------------------------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------------------------

@app.post("/parking-slots", status_code=201)
def create_parking_slot(
    payload: ParkingSlotCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Thêm mới một vị trí đỗ xe."""
    new_slot = ParkingSlot(
        slot_code=payload.slot_code,
        zone_name=payload.zone_name,
        max_weight=payload.max_weight,
        is_available=payload.is_available if payload.is_available is not None else True,
    )

    try:
        db.add(new_slot)
        db.commit()
        db.refresh(new_slot)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Mã vị trí đỗ (slot_code) đã tồn tại",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Lỗi cơ sở dữ liệu, vui lòng thử lại",
        )

    data = ParkingSlotResponse.model_validate(new_slot).model_dump()
    return json_response(
        status_code=201,
        message="Thêm vị trí đỗ xe thành công",
        error=None,
        data=data,
        path=str(request.url.path),
    )


@app.get("/parking-slots")
def get_parking_slots(request: Request, db: Session = Depends(get_db)):
    """Lấy danh sách toàn bộ vị trí đỗ xe."""
    slots = db.query(ParkingSlot).all()
    data = [ParkingSlotResponse.model_validate(s).model_dump() for s in slots]

    return json_response(
        status_code=200,
        message="Lấy danh sách vị trí đỗ xe thành công",
        error=None,
        data=data,
        path=str(request.url.path),
    )


@app.get("/parking-slots/{slot_id}")
def get_parking_slot_detail(
    slot_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Lấy thông tin chi tiết một vị trí đỗ xe theo id."""
    slot = db.query(ParkingSlot).filter(ParkingSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(status_code=404, detail="Parking slot not found")

    data = ParkingSlotResponse.model_validate(slot).model_dump()
    return json_response(
        status_code=200,
        message="Lấy thông tin vị trí đỗ xe thành công",
        error=None,
        data=data,
        path=str(request.url.path),
    )
