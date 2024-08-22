"""
Module is responsible for creating a connection pool to the database and creating tables
using the schema.sql file. It also provides a context manager to get a connection
from the pool.
"""

from pathlib import Path
import os
from contextlib import asynccontextmanager
import asyncpg
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

PGHOST = os.getenv("PGHOST")
PGUSER = os.getenv("PGUSER")
PGPORT = os.getenv("PGPORT")
PGPASSWORD = os.getenv("PGPASSWORD")
PGDATABASE = os.getenv("PGDATABASE")
DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
##DATABASE_URL = "postgresql://admin:test_password@db/postgres"


class Database:
    """The class to connect to db."""

    _pool = None

    @classmethod
    async def init(cls):
        """
        Initializes the database connection pool.

        Args:
            cls: The class object.

        Returns:
            None
        """
        cls._pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=10)
        print("Database connection pool created")

    @classmethod
    async def release_connection(cls, connection):
        """
        Releases a connection back to the connection pool.

        Args:
            cls: The class object.
            connection: The connection to be released.

        Returns:
            None
        """
        await cls._pool.release(connection)
        print("Connection released")

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        """
        Gets a connection from the connection pool.

        Args:
            cls: The class object.

        Yields:
            connection: The connection object.

        Returns:
            None
        """
        connection = await cls._pool.acquire()
        try:
            yield connection
        finally:
            await cls.release_connection(connection)

    @classmethod
    async def create_tables(cls):
        """
        Creates tables in the database using the schema.sql file.

        Args:
            cls: The class object.

        Returns:
            None
        """
        print("Creating tables")
        file_path = BASE_DIR / "app" / "schema.sql"
        file_ = open(file_path, "r", encoding="utf-8")
        SCHEMA_SQL = file_.read()
        async with cls.get_connection() as connection:
            await connection.execute(SCHEMA_SQL)
            print("Tables created successfully")
        file_.close()
        print("Finished creating tables")


@asynccontextmanager
async def get_db():
    """
    Context manager to get a database connection.

    Yields:
        connection: The database connection object.

    Returns:
        None
    """
    async with Database.get_connection() as connection:
        yield connection
