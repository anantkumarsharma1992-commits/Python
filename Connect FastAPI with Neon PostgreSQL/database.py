"""
database.py

Same create_engine + sessionmaker setup your instructor built live in class -
but with ONE deliberate change: the connection string now comes from a .env
file instead of being typed directly into this .py file.

Your class's original databaseops.py had this line:
    DATABASE_URL = 'postgresql://neondb_owner:<password>@...'

That's a real password sitting in plain text, in a file that could easily
get uploaded, screenshotted, or committed to GitHub - exactly what happened
with your own uploaded files for this task. This is the fix.
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
