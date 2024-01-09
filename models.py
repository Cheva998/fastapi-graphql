from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import declarative_base, sessionmaker, Session


SQLALCHEMY_DATABASE_URL = "sqlite:///example.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base: DeclarativeMeta = declarative_base()


class Item(Base):
    __tablename__= 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)