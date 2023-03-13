from fastapi import FastAPI
from fastapi import Depends, status, Response, HTTPException
import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from postgresdb import SessionLocal as postgres_session,engine as postgres_engine,Base as postgres_base
from mysqldb import SessionLocal as mysql_session,engine as mysql_engine,Base as mysql_base
from sqlalchemy import select
from sqlalchemy import desc


app = FastAPI(
    title= "Megafon_wallet",
    description = "This project handles payment with wallet"
)


@app.on_event("startup")
async def startup():
    async with postgres_engine.begin() as conn:
        await conn.run_sync(postgres_base.metadata.create_all)
    await startup_mysql()


async def startup_mysql():
    async with mysql_engine.begin() as conn:
        await conn.run_sync(mysql_base.metadata.create_all)


async def get_postgres_db():
    db_session = postgres_session()
    try:
        yield db_session
    finally:
        await db_session.close()

async def get_mysql_db():
    db_session = mysql_session()
    try:
        yield db_session
    finally:
        await db_session.close()



#GET and POST api for Wallet
# api to get all wallets
@app.get('/wallets', status_code=status.HTTP_200_OK, tags=['wallet'])
async def all_wallets():
    async with postgres_session() as session:
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
    async with postgres_session() as session:
        networks = await session.execute(select(models.Mobile_Network).order_by(models.Mobile_Network.id))
    return networks.scalars().all()

#api to get all paid for Mavji Somon
@app.get('/mavji_somon', status_code=status.HTTP_200_OK, tags=['mavji_somon'])
async def all_mavji_somon():
    async with postgres_session() as session:
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
    async with postgres_session() as session:
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
    async with postgres_session() as session:
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

# api to get all wallets
@app.get('/mysql_wallet', status_code=status.HTTP_200_OK, tags=['wallet_mysql'])
async def all_wallets():
    async with mysql_session() as session:
        wallets = await session.execute(select(models.Wallet).order_by(models.Wallet.id))
    return wallets.scalars().all()


# api to get the wallet by id
@app.get('/mysql_wallet/{id}', status_code=status.HTTP_200_OK, tags=['wallet_mysql'])
async def get_wallet(id:int, response: Response, db: AsyncSession = Depends(get_mysql_db)):
    wallet = await db.execute(select(models.Wallet).where(models.Wallet.id == id))
    wallet = wallet.scalar()               
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Wallet with an id {id} is not available')
    return wallet


# api to create a wallet
@app.post('/mysql_wallet', status_code=status.HTTP_201_CREATED, tags=['wallet_mysql'])
async def create_wallet(request: schemas.Wallet, db: AsyncSession = Depends(get_mysql_db)):
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


# api to get all paid dodopizza
@app.get('/dodo_pizza', status_code=status.HTTP_200_OK, tags=['dodo_pizza'])
async def dodo_pizza():
    async with mysql_session() as session:
        all_dodopizza = await session.execute(select(models.DodoPizza).order_by(models.DodoPizza.id))
    return all_dodopizza.scalars().all()




# api to pay for dodopizza
@app.post('/dodo_pizza', status_code=status.HTTP_202_ACCEPTED, tags=['dodo_pizza'])
async def dodo_pizza_pay(request: schemas.DodoPizza, db: AsyncSession = Depends(get_mysql_db)):
    last_wallet = await db.execute(select(models.Wallet).order_by(desc(models.Wallet.id)).limit(1))
    last_wallet = last_wallet.scalar_one()
    if last_wallet.balance >= request.payment_sum:
        new_balance = last_wallet.balance - request.payment_sum
        dodo_pizza = models.DodoPizza(order_number=request.order_number,
                                          payment_sum=request.payment_sum)
        
        last_wallet.balance = new_balance
        await db.commit()
        db.add(dodo_pizza)
        await db.commit()
        await db.refresh(dodo_pizza)
        return dodo_pizza
    
    else:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED,
                            detail=f'{"You dont have enough balance"}')
    




    








