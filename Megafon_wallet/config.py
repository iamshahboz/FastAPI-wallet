from pydantic import BaseModel

class Postgresdb(BaseModel):
    postgresql_url: str 

class Mysqldb(BaseModel):
    mysql_url: str 



