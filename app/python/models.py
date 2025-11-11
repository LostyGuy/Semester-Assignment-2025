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
    __tablename__ = "profile_data"
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
    project_title: str = Column(
        String(20), 
        index=True
        )
    project_content: str = Column(
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
    token_value: int = Column(
        String,
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
    status: str = Column(
        String,
        index=True,
        default="accessible"
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
        index=True,
        nullable= False,   
    )
    PRIVATE_JWT_KEY: str = Column(
        String,
        index= True,
        nullable= False,
    )