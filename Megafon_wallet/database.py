
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import toml

config_data = toml.load('settings.toml')


SQLALCHEMY_POSTGRES_DATABASE_URL = config_data['database']['postgresql_url']
engine = create_async_engine(
SQLALCHEMY_POSTGRES_DATABASE_URL, connect_args={})




SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()







