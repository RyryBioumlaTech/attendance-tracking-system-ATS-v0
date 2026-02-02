
import sys
from sqlalchemy import create_engine, text

DATABASE_URI = 'mysql+pymysql://root:@localhost/gpDb'

try:
    engine = create_engine(DATABASE_URI)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        conn.commit()
    print("Dropped alembic_version table.")
except Exception as e:
    print(f"Error: {e}")
