from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True, index=True)  # индекс разрешаем для быстрого поиска
    author = Column(String)
    created_at = Column(DateTime)

    # отношения с другими моделями
    values = relationship("Value", back_populates="file", cascade="all, delete")
    result = relationship("Result", back_populates="file", uselist=False, cascade="all, delete")

class Value(Base):
    __tablename__ = "values"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    start_time = Column(DateTime)  # TODO: что делать при одинаком времени?
    duration = Column(Integer)
    value = Column(Float)

    # отношение с моделью File
    file = relationship("File", back_populates="values")

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"), unique=True)
    first_start = Column(DateTime)
    last_start = Column(DateTime)
    min_duration = Column(Integer)
    max_duration = Column(Integer)
    avg_duration = Column(Integer)
    avg_value = Column(Float)
    median_value = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)
    experiment_count = Column(Integer)

    # отношение с моделью File
    file = relationship("File", back_populates="result")