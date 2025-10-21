from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from python.database import Base

class users(Base):
    __tablename__ = "users"
    ID: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
        )
    nickname: str = Column(
        String(20),
        index=True
        )
    email: str = Column(
        String(20),
        index=True
        )
    hashed_password: str = Column(
        String(30),
        index=True
        )
    time_stamp: str = Column(
        String(10),
        index=True
        )
    
class profile(Base):
    __tablename__ = "profiles"
    ID: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
        )
    user_ID : int = Column(
        Integer,
        index=True)
    content: str = Column(
        String(20),
        index=True
        )
    time_stamp: str = Column(
        String(10),
        index=True
        )