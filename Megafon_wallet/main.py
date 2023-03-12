from fastapi import FastAPI
from fastapi import Depends, status, Response, HTTPException
import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal,engine,Base
from sqlalchemy import select




app = FastAPI(
    title= "Megafon_wallet",
    description = "This project handles payment with wallet"
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_postgres_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        await db_session.close()

#GET and POST api for Wallet
# api to get all wallets
@app.get('/wallets', status_code=status.HTTP_200_OK, tags=['wallet'])
async def all_wallets():
    async with SessionLocal() as session:
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
@app.post('/mobile_network',status_code = status.HTTP_202_ACCEPTED,tags=['mobile network'])
async def network_pay(request:schemas.Mobile_Network,db:AsyncSession=Depends(get_postgres_db)):
    last_wallet = await db.execute(select(models.Wallet).order_by(models.Wallet.id).order_by(models.Wallet.id))
    if last_wallet.balance >= schemas.Mobile_Network.payment_sum:
        new_balance = last_wallet.balance - 






