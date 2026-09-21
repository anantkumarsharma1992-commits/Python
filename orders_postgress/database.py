"""
database.py

Builds the connection to the real PostgreSQL database (hosted on Neon).
The connection string is loaded from a .env file - never typed directly
into this file - so it can never be accidentally committed to GitHub.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env and paste in "
        "your real Neon connection string there."
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
