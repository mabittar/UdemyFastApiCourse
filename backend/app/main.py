import logging

import config
import databases
import sqlalchemy
from fastapi import FastAPI, Request

from .models.books import BookModel, BookRequest

logger = logging.getLogger(__name__)

# DATABASE_URL = f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_SERVER}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"

database = databases.Database(config.DATABASE_URL)
metadata = sqlalchemy.MetaData()


books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("author", sqlalchemy.String),
    sqlalchemy.Column("pages", sqlalchemy.Integer, default=0),
)

readers = sqlalchemy.Table(
    "readers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
)

readers_books = sqlalchemy.Table(
    "readers_books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("book_id", sqlalchemy.ForeignKey("books.id"), nullable=False),
    sqlalchemy.Column("readers_id", sqlalchemy.ForeignKey("readers.id"), nullable=False),
)


# engine = sqlalchemy.create_engine(config.DATABASE_URL)
# metadata.create_all(engine)


app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)


@app.on_event("startup")
async def start_up():
    logger.info("STARTING APP and connect to database")
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    logger.info("SHUTDOWN APP and disconnect from Database")
    await database.disconnect()


@app.get("/books/")
async def get_all_books():
    logger.info("List all books from Database")
    query = books.select()
    return await database.fetch_all(query)


@app.post("/books/")
async def create_book(book: BookRequest) -> dict:

    logger.info("Insert new book to database")
    query = books.insert().values(book.dict())
    book_model_id = await database.execute(query)
    logger.info(f"Database committed, returning book id {book_model_id}")

    return {"id": book_model_id}

@app.post("/readers/")
async def create_readers(request: Request):
    data = await request.json()
    logger.info("Insert new reader to database")
    query = readers.insert().values(**data)
    reader_id = await database.execute(query)
    logger.info(f"Database committed, returning reader id {reader_id}")

    return {"id": reader_id}

@app.post("/read/")
async def read_book(request: Request):
    data = await request.json()
    logger.info("Create new relationship between reader and book.")
    query = readers_books.insert().values(**data)
    reader_id = await database.execute(query)
    logger.info(f"Database committed, returning reader id {reader_id}")

    return {"id": reader_id}

