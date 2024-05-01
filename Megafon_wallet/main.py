from fastapi import FastAPI
from fastapi import Depends, status, Response, HTTPException
import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc
import asyncio
from time import time
import aiohttp
from sqlalchemy import select
import uvicorn



app = FastAPI(
    title= "Megafon_wallet",
    description = "This project handles payment with wallet"
)




from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import toml

# Load database configuration from settings.toml
config_data = toml.load('settings.toml')
SQLALCHEMY_POSTGRES_DATABASE_URL = config_data['database']['postgresql_url']

# Create the async database engine
engine = create_async_engine(SQLALCHEMY_POSTGRES_DATABASE_URL)

# Create a sessionmaker for async sessions
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_postgres_db():
    async with async_session() as session:
        yield session


@app.get("/", tags=["homepage"])
async def homepage()-> dict:
    return {"message": "Welcome to the home page"}




#GET and POST api for Wallet
# api to get all wallets
@app.get('/wallets', status_code=status.HTTP_200_OK, tags=['wallet'])
async def all_wallets():
    async with get_postgres_db() as session:
        wallets = await session.execute(select(models.Wallet).order_by(models.Wallet.id))
    return wallets.scalars().all()


# api to get the wallet by id
@app.get('/wallet/{id}', status_code=status.HTTP_200_OK, tags=['wallet'])
async def get_wallet(id:int, response: Response, db: AsyncSession = Depends(get_postgres_db)):
    wallet = await db.execute(select(models.Wallet).where(models.Wallet.id == id))
    wallet = wallet.scalar()               
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Wallet with an id {id} is not available')
    return wallet


# api to create a wallet
@app.post('/wallet', status_code=status.HTTP_201_CREATED, tags=['wallet'])
async def create_wallet(request: schemas.Wallet, db: AsyncSession = Depends(get_postgres_db)):
    user_exists = await db.execute(select(models.Wallet).where(models.Wallet.phone_number==request.phone_number))
    if user_exists.scalar():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="This phone number is already registered")
    
    new_wallet = models.Wallet(phone_number=request.phone_number,
                             balance=request.balance)
# if we don't add and commit the query to the db it will not be added
    db.add(new_wallet)
    await db.commit()
    await db.refresh(new_wallet)
    return new_wallet

# api to pay for Mobile Network
@app.post('/mobile_network', status_code=status.HTTP_202_ACCEPTED, tags=['mobile_network'])
async def network_pay(request: schemas.Mobile_Network, db: AsyncSession = Depends(get_postgres_db)):
    last_wallet = await db.execute(select(models.Wallet).order_by(desc(models.Wallet.id)).limit(1))
    last_wallet = last_wallet.scalar_one()
    if last_wallet.balance >= request.payment_sum:
        new_balance = last_wallet.balance - request.payment_sum
        mobile_network = models.Mobile_Network(phone_number=request.phone_number,
                                               payment_sum=request.payment_sum)
        
        last_wallet.balance = new_balance
        await db.commit()
        db.add(mobile_network)
        await db.commit()
        await db.refresh(mobile_network)
        return mobile_network
    
    else:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED,
                            detail=f'{"You dont have enough balance"}')

# api to get the list of paid mobile network  
@app.get('/mobile_network',status_code = status.HTTP_200_OK,tags=['mobile_network'])
async def all_networks():
    async with get_postgres_db() as session:
        networks = await session.execute(select(models.Mobile_Network).order_by(models.Mobile_Network.id))
    return networks.scalars().all()

#api to get all paid for Mavji Somon
@app.get('/mavji_somon', status_code=status.HTTP_200_OK, tags=['mavji_somon'])
async def all_mavji_somon():
    async with get_postgres_db() as session:
        mavjisomon = await session.execute(select(models.Mavgi_Somon).order_by(models.Mavgi_Somon.id))
    return mavjisomon.scalars().all()

#api for pay for Mavji Somon
@app.post('/mavji_somon', status_code=status.HTTP_202_ACCEPTED, tags=['mavji_somon'])
async def mavji_somon_pay(request: schemas.Mavgi_Somon, db: AsyncSession = Depends(get_postgres_db)):
    last_wallet = await db.execute(select(models.Wallet).order_by(desc(models.Wallet.id)).limit(1))
    last_wallet = last_wallet.scalar_one()
    if last_wallet.balance >= request.payment_sum:
        new_balance = last_wallet.balance - request.payment_sum
        mavji_somon = models.Mavgi_Somon(account_number=request.account_number,
                                         payment_sum=request.payment_sum)
        
        last_wallet.balance = new_balance
        await db.commit()
        db.add(mavji_somon)
        await db.commit()
        await db.refresh(mavji_somon)
        return mavji_somon
    
    else:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED,
                            detail=f'{"You dont have enough balance"}')
    
#api to get all paid for Shabakatj
@app.get('/shabakatj', status_code=status.HTTP_200_OK, tags=['shabakatj'])
async def all_shabakatj():
    async with get_postgres_db() as session:
        shabakatj = await session.execute(select(models.Shabakatj).order_by(models.Shabakatj.id))
    return shabakatj.scalars().all()

# api to pay for Shabakatj
@app.post('/shabakatj', status_code=status.HTTP_202_ACCEPTED, tags=['shabakatj'])
async def shabakatj_pay(request: schemas.Shabakatj, db: AsyncSession = Depends(get_postgres_db)):
    last_wallet = await db.execute(select(models.Wallet).order_by(desc(models.Wallet.id)).limit(1))
    last_wallet = last_wallet.scalar_one()
    if last_wallet.balance >= request.payment_sum:
        new_balance = last_wallet.balance - request.payment_sum
        shabakatj = models.Shabakatj(account_number=request.account_number,
                                     payment_sum=request.payment_sum)
        
        last_wallet.balance = new_balance
        await db.commit()
        db.add(shabakatj)
        await db.commit()
        await db.refresh(shabakatj)
        return shabakatj
    
    else:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED,
                            detail=f'{"You dont have enough balance"}')
    
# api to get all Khayriyai_Ozod
@app.get('/khayriyai_ozod', status_code=status.HTTP_200_OK, tags=['khayriyai_ozod'])
async def all_khayriyai_ozod():
    async with get_postgres_db() as session:
        khayriyai_ozod = await session.execute(select(models.Khayriyai_Ozod).order_by(models.Khayriyai_Ozod.id))
    return khayriyai_ozod.scalars().all()

# api to pay for Khayriyai_Ozod
@app.post('/khayriyai_ozod', status_code=status.HTTP_202_ACCEPTED, tags=['khayriyai_ozod'])
async def khayriyai_ozod_pay(request: schemas.Khayriyai_Ozod, db: AsyncSession = Depends(get_postgres_db)):
    last_wallet = await db.execute(select(models.Wallet).order_by(desc(models.Wallet.id)).limit(1))
    last_wallet = last_wallet.scalar_one()
    if last_wallet.balance >= request.payment_sum:
        new_balance = last_wallet.balance - request.payment_sum
        khayriyai_ozod = models.Khayriyai_Ozod(phone_number=request.phone_number,
                                                payment_sum=request.payment_sum)
        
        last_wallet.balance = new_balance
        await db.commit()
        db.add(khayriyai_ozod)
        await db.commit()
        await db.refresh(khayriyai_ozod)
        return khayriyai_ozod
    
    else:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED,
                            detail=f'{"You dont have enough balance"}')
    

#the api's below will be executed in Mysql database


# #api to send http request to internal servers



@app.get("/cat_fact",tags=['aiohttp_request'])
async def get_cat_fact():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://cat-fact.herokuapp.com/facts/") as response:
            data = await response.json()
            return data
        

@app.get("/quotes",tags=['aiohttp_request'])
async def get_quotes():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://ron-swanson-quotes.herokuapp.com/v2/quotes") as response:
            data = await response.json()
            return data
        

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=1010)




    




    








