from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Equipment(SQLModel, table = True):
    id: int
    serial_number: str
    make: str
    model: str
    address: str
    city: str
    state: str
    zip: int
    location: str
    ip_address: str
    mac_address: str 

postgres_sql_file_name = 'printers.db'
postgres_url = f'postgresql://postgres:postgres@localhost:5432/{postgres_sql_file_name}'

connect_args = {"check_same_thread": False}
engine = create_engine(postgres_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()