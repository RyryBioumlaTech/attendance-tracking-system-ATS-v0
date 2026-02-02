
import sys
from sqlalchemy import create_engine, inspect, text

# Connection string from app/__init__.py
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/gpDb'
DATABASE_URI = 'mysql+pymysql://root:@localhost/gpDb'

try:
    engine = create_engine(DATABASE_URI)
    inspector = inspect(engine)
    
    print("--- TABLES ---")
    tables = inspector.get_table_names()
    print(tables)
    
    if 'alembic_version' in tables:
        print("\n--- ALEMBIC VERSION ---")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM alembic_version"))
            for row in result:
                print(row)
    else:
        print("\nExisting tables found (but no alembic_version):", len(tables) > 0)
        
except Exception as e:
    print(f"Error connecting to database: {e}")
