from sqlalchemy import Column, Integer, String, DateTime
from databases.db import Base
from datetime import datetime

class LogData(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    log_action = Column(String)
    message = Column(String)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<LogData {self.id}>"
    
    def __str__(self):
        return f"<LogData {self.id}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "log_level": self.log_action,
            "message": self.message,
            "created_at": self.created_at
        }