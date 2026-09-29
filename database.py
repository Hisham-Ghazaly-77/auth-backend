from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os


# Load variables from .env
load_dotenv()


# Database settings from .env
SERVER = os.getenv("DB_SERVER")
DATABASE = os.getenv("DB_NAME")


# SQL Server connection string
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)


# Encode connection string
connection_url = (
    f"mssql+pyodbc:///?odbc_connect="
    f"{quote_plus(connection_string)}"
)


# Create database engine
engine = create_engine(connection_url)