# importing dependencies
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from postgresdb import Base as postgresbase
from sqlalchemy.orm import relationship


# Models with required fields
# The models below till DodoPizza will be stored in PostgreSQL database including Wallet
class Wallet(postgresbase):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(Integer, unique=True)
    balance = Column(Integer, nullable=False)


class Mobile_Network(postgresbase):
    __tablename__ = 'mobile_networks'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Mavgi_Somon(postgresbase):
    __tablename__ = "mavgi_somon"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Shabakatj(postgresbase):
    __tablename__= "shabakatj"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Khayriyai_Ozod(postgresbase):
    __tablename__= "khayriyai_ozod"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)

# The models belove will be stored in MySQL database, including Wallet model
class DodoPizza(postgresbase):
    __tablename__= "dodopizza"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)
 

class Salomat_tj(postgresbase):
    __tablename__= "salomat_tj"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Kitobz(postgresbase):
    __tablename__= "kitobz"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)


class Tojnet(postgresbase):
    __tablename__= "tojnet"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(Integer,nullable=False)
    payment_sum = Column(Integer,nullable=False)
    



        


