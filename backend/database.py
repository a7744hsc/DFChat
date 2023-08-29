from typing import List
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, joinedload,subqueryload
import shutil
import logging
from config import RECORD_NAME_MAX_LEN

logger = logging.getLogger(__name__)

# 创建SQLite数据库引擎和会话工厂
engine = create_engine("sqlite:///mydb.db", pool_size=20, max_overflow=0)
# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建ORM基类和用户模型
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
    dialogs = relationship("DialogRecord", back_populates="user")

    @staticmethod
    def get_user_by_user_name(username: str):
        session = SessionLocal()
        user = session.query(User).filter(User.username == username).first()
        session.close()
        return user

    @staticmethod
    def create_user(username: str, password: str, email: str):
        session = SessionLocal()
        user = User(username=username, password=password, email=email)
        session.add(user)
        session.commit()
        session.refresh(user)
        session.close()
        return user


class DialogRecord(Base):
    __tablename__ = "dialogrecords"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="dialogs")
    dialog_content = Column(Text)
    file_path = Column(Text)
    record_name = Column(String(RECORD_NAME_MAX_LEN))

    @staticmethod
    def get_record_by_id(session_id: int) -> "DialogRecord":
        session = SessionLocal()
        record:DialogRecord = session.query(DialogRecord).filter(DialogRecord.id == session_id).options(joinedload(DialogRecord.user)).first()
        session.close()
        return record
    
    @staticmethod
    def get_record_by_username(username: str) -> List["DialogRecord"]:
        session = SessionLocal()
        user = session.query(User).filter(User.username == username).options(subqueryload(User.dialogs)).first()
        session.close()
        return user.dialogs
    
    @staticmethod
    def create_record(user_id: int, dialog_content: str, record_name: str, file_path: str | None = None):
        session = SessionLocal()
        # length limit
        record_name = record_name[:RECORD_NAME_MAX_LEN]
        dialog = DialogRecord(user_id=user_id, dialog_content=dialog_content, file_path=file_path, record_name=record_name)
        session.add(dialog)
        session.commit()
        session.refresh(dialog)
        session.close()
        return dialog
    
    @staticmethod
    def update_record(session_id: int, dialog_content: str, file_path: str | None = None, record_name: str | None = None):
        session = SessionLocal()
        record = session.query(DialogRecord).filter(DialogRecord.id == session_id).first()
        if not record:
            session.close()
            raise Exception("Record not found")
        
        record.dialog_content = dialog_content
        if file_path:
            record.file_path = file_path
        if record_name:
            record.record_name = record_name
        session.commit()
        session.refresh(record)   
        session.close()
        return record
    
    @staticmethod
    def update_record_name(session_id: int, record_name: str):
        session = SessionLocal()
        record = session.query(DialogRecord).filter(DialogRecord.id == session_id).first()
        record.record_name = record_name[:RECORD_NAME_MAX_LEN]
        session.commit()
        session.refresh(record)   
        session.close()
        return True

    @staticmethod
    def delete_by_id(session_id: int):
        session = SessionLocal()
        session_obj = session.query(DialogRecord).filter(DialogRecord.id == session_id).first()
        # delete all files related to this session
        file_dir = session_obj.file_path
        if file_dir:
            try:
                shutil.rmtree(file_dir)
            except Exception as e:
                logger.exception(e)
        if session_obj:
            session.delete(session_obj)
            session.commit()
        else:
            session.close()
            raise Exception("Session not found")
        session.close()
        return True


# 创建数据库表
Base.metadata.create_all(bind=engine)



