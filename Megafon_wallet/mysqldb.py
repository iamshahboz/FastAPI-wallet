
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import toml

# this is for security reason
config_data = toml.load('settings.toml')

#this is for postgresdb
SQLALCHEMY_MYSQL_DATABASE_URL = config_data['database']['mysql_url']
engine = create_async_engine(
SQLALCHEMY_MYSQL_DATABASE_URL, connect_args={})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()
















