from database import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DB_NAME()"))
        database_name = result.scalar()

        print("Database connected successfully!")
        print("Connected to:", database_name)

except Exception as error:
    print("Database connection failed!")
    print(error)