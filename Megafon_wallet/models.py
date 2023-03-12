# importing dependencies
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base
from sqlalchemy.orm import relationship


# Models with required fields
# The models below till DodoPizza will be stored in PostgreSQL database including Wallet
class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(Integer, unique=True)
    balance = Column(Integer, nullable=False)


class Mobile_Network(Base):
    __tablename__ = 'mobile_networks'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Mavgi_Somon(Base):
    __tablename__ = "mavgi_somon"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Shabakatj(Base):
    __tablename__= "shabakatj"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Khayriyai_Ozod(Base):
    __tablename__= "khayriyai_ozod"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)

# The models belove will be stored in MySQL database, including Wallet model
class DodoPizza(Base):
    __tablename__= "dodopizza"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)
 

class Salomat_tj(Base):
    __tablename__= "salomat_tj"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Kitobz(Base):
    __tablename__= "kitobz"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Tojnet(Base):
    __tablename__= "tojnet"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)
    



        


