import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import urllib.parse
load_dotenv()

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
driver = os.getenv("DB_DRIVER")
encrypt = os.getenv("DB_ENCRYPT")
trust = os.getenv("DB_TRUST")

params = urllib.parse.quote_plus(
    f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt={encrypt};TrustServerCertificate={trust};"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
