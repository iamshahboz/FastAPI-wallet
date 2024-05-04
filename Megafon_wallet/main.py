from fastapi import FastAPI
from fastapi import Depends, status, Response, HTTPException
import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc
import aiohttp
from sqlalchemy import select
import uvicorn

from datetime import datetime, timedelta, timezone 
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI(
    title= "Megafon_wallet",
    description = "This project handles payment with wallet"
)




from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import toml



SECRET_KEY = "8248d76de770ff303d350c27e268f0638b62f15482b125e300684249907b02d4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDb(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDb(**user_dict)
    
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username = token_data.username)  
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]

):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user

@app.post('/token')
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
)-> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect username or password",
            headers= {"WWW-Authenticate": "Bearer"},

        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/", response_model = User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],

):
    return current_user

@app.get("/users/me/items")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item": "Foo", "owner": current_user.username}]
    







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
    uvicorn.run("main:app", host="0.0.0.0", port=1010, reload=True)
    







    




    








