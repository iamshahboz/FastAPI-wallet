from pydantic import BaseModel, Field
from typing import Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Float


'''
Schema is a validator for our models
'''

class Wallet(BaseModel):
    phone_number: int
    balance: float

    class Config:
        orm_mode = True


class Mobile_Network(BaseModel):
    phone_number: int 
    payment_sum : int = Field(..., min_value=0)

    class Config:
        orm_mode = True  

class Mavgi_Somon(BaseModel):
    account_number: int 
    payment_sum : int = Field(..., min_value=0)
    
    class Config:
        orm_mode = True  

class Shabakatj(BaseModel):
    account_number: int
    payment_sum : int = Field(..., min_value=0)

    class Config:
        orm_mode = True  

class Khayriyai_Ozod(BaseModel):
    phone_number:int 
    payment_sum:int = Field(..., min_value=0) 
    
    class Config:
        orm_mode = True  
        
class DodoPizza(BaseModel):
    order_number:int 
    payment_sum: int = Field(..., min_value=0) 

    class Config:
        orm_mode = True  

class Kitobz(BaseModel):
    number: int 
    payment_sum: int = Field(..., min_value=0)

    class Config:
        orm_mode = True 

class Tojnet(BaseModel):
    account_number: int 
    payment_sum: int = Field(..., min_value=0) 

    class Config:
        orm_mode = True 


