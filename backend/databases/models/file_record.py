from sqlalchemy import Column, Integer, String, DateTime, Float
from databases.db import Base
from datetime import datetime

class FileRecord(Base):
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    received_date = Column(DateTime, default=datetime.now(), nullable=True)
    question = Column(String, nullable=True)
    details = Column(String, nullable=True)
    rnd = Column(Float, nullable=True)
