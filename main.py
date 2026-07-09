from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime, timezone

from database import get_db
from models import ParkingSlotModel
from schemas import ParkingSlotCreate

app = FastAPI()


# ----------------- HELPER -----------------
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_response(status_code: int, message: str, error, data, path: str):
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": now_iso()
    }


def serialize_slot(slot: ParkingSlotModel):
    return {
        "id": slot.id,
        "slot_code": slot.slot_code,
        "zone_name": slot.zone_name,
        "max_weight": slot.max_weight,
        "is_available": bool(slot.is_available)
    }


# ----------------- GLOBAL EXCEPTION HANDLERS -----------------
# Đảm bảo mọi lỗi (business hoặc validation) đều trả về đúng cấu trúc 6 trường,
# không lộ Stack Trace thô ra ngoài.

ERROR_TEXT_MAP = {
    400: "Bad Request",
    404: "Not Found",
    409: "Conflict",
    422: "Unprocessable Entity",
    500: "Internal Server Error"
}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=build_response(
            status_code=exc.status_code,
            message=exc.detail,
            error=ERROR_TEXT_MAP.get(exc.status_code, "Error"),
            data=None,
            path=str(request.url.path)
        )
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Bắt lỗi validate của Pydantic (zone_name < 3 ký tự, max_weight <= 0, thiếu field...)
    first_error = exc.errors()[0]
    field = ".".join(str(loc) for loc in first_error["loc"] if loc != "body")
    message = f"Dữ liệu không hợp lệ tại trường '{field}': {first_error['msg']}"

    return JSONResponse(
        status_code=422,
        content=build_response(
            status_code=422,
            message=message,
            error="Unprocessable Entity",
            data=None,
            path=str(request.url.path)
        )
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=build_response(
            status_code=500,
            message="Lỗi hệ thống, vui lòng thử lại sau",
            error="Internal Server Error",
            data=None,
            path=str(request.url.path)
        )
    )


# ----------------- API ENDPOINTS -----------------

@app.post("/parking-slots", status_code=201)
def create_parking_slot(payload: ParkingSlotCreate, request: Request, db: Session = Depends(get_db)):
    new_slot = ParkingSlotModel(
        slot_code=payload.slot_code,
        zone_name=payload.zone_name,
        max_weight=payload.max_weight,
        is_available=payload.is_available
    )

    try:
        db.add(new_slot)
        db.commit()
        db.refresh(new_slot)

    except IntegrityError:
        # Bẫy dữ liệu: slot_code trùng lặp -> vi phạm ràng buộc UNIQUE
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Mã vị trí đỗ xe đã tồn tại"
        )

    except SQLAlchemyError:
        # Sự cố nghẽn mạch / lỗi kết nối DB -> rollback để bảo toàn dữ liệu
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Lỗi hệ thống khi lưu dữ liệu"
        )

    return JSONResponse(
        status_code=201,
        content=build_response(
            status_code=201,
            message="Thêm vị trí đỗ xe thành công",
            error=None,
            data=serialize_slot(new_slot),
            path=str(request.url.path)
        )
    )


@app.get("/parking-slots")
def get_all_parking_slots(request: Request, db: Session = Depends(get_db)):
    slots = db.query(ParkingSlotModel).all()  # lấy danh sách toàn bộ -> chấp nhận .all() vì đây là API list
    data = [serialize_slot(s) for s in slots]

    return JSONResponse(
        status_code=200,
        content=build_response(
            status_code=200,
            message="Lấy danh sách vị trí đỗ xe thành công",
            error=None,
            data=data,
            path=str(request.url.path)
        )
    )


@app.get("/parking-slots/{slot_id}")
def get_parking_slot_detail(slot_id: int, request: Request, db: Session = Depends(get_db)):
    # Tối ưu: chỉ SELECT đúng 1 bản ghi qua .filter().first()
    slot = db.query(ParkingSlotModel).filter(ParkingSlotModel.id == slot_id).first()

    if slot is None:
        raise HTTPException(status_code=404, detail="Parking slot not found")

    return JSONResponse(
        status_code=200,
        content=build_response(
            status_code=200,
            message="Lấy thông tin vị trí đỗ xe thành công",
            error=None,
            data=serialize_slot(slot),
            path=str(request.url.path)
        )
    )