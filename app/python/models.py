from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, Boolean
from python.database import Base

class users(Base):
    __tablename__ = "users"
    ID: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        )
    nickname: str = Column(
        String(20),
        index=True,
        )
    email: str = Column(
        String(20),
        index=True,
        )
    hashed_password: str = Column(
        String(30),
        index=True,
        )
    time_stamp: str = Column(
        TIMESTAMP,
        index=True,
        )
    
class profile(Base):
    __tablename__ = "profiles"
    ID: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        )
    user_ID : int = Column(
        Integer,
        index=True,
        )
    content: str = Column(
        String(20),
        index=True,
        )
    time_stamp: str = Column(
        TIMESTAMP,
        index=True,
        )
    
class session(Base):
    __tablename__ = "session"
    ID: int = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    user_ID: int = Column(
        Integer,
        index=True,
    )
    hash_user_ID: int = Column(
        Integer,
        index=True,
    )
    time_stamp: str = Column(
        TIMESTAMP,
        index=True,
    )
    token_expires: str = Column(
        TIMESTAMP,
        index=True,
    )
    
class secret(Base):
    __tablename__ = "7365637265745f64617461"
    ID: int = Column(
        Integer,
        index = True,
        primary_key = True,
        unique = True,
        autoincrement= True,
    )
    SECRET_SALT_KEY: str = Column(
        String,
        nullable= False,   
    )
    