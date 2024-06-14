# importing dependencies
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from enum import Enum 
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()
metadata = Base.metadata



class User(Base):
    '''
    User model
    '''
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(Integer, nullable=False, unique=True)
    balance = Column(Float, nullable=False)
    password_hash = Column(String)
    created_date = Column(DateTime(timezone=True), default=func.now())
    
    
class TransactionStatus(Enum):
    FAILED = 'Failed'
    PENDING = 'Pending'
    SUCCESS = 'Success'
       
    
class Transaction(Base):
    '''
    Transaction model
    '''
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(Integer, ForeignKey('users.id'))
    receiver = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    created_date = Column(DateTime(timezone=True), default=func.now())
    status = Column(Enum(TransactionStatus))
    


    



        


