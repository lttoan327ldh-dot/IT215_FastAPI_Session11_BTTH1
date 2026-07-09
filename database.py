import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cấu hình kết nối MySQL - có thể override bằng biến môi trường DATABASE_URL
# Ví dụ: mysql+pymysql://<user>:<password>@<host>:<port>/<database>
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/parking_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency cung cấp session DB cho từng request, tự đóng khi xong."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
