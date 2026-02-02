
import sys
from sqlalchemy import create_engine, inspect, text

DATABASE_URI = 'mysql+pymysql://root:@localhost/gpDb'

try:
    engine = create_engine(DATABASE_URI)
    inspector = inspect(engine)
    
    with open('db_info.txt', 'w') as f:
        f.write("--- TABLES ---\n")
        tables = inspector.get_table_names()
        f.write(str(tables) + "\n")
        
        if 'alembic_version' in tables:
            f.write("\n--- ALEMBIC VERSION ---\n")
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM alembic_version"))
                for row in result:
                    f.write(str(row) + "\n")
        else:
            f.write("\nNO alembic_version table found.\n")
            
except Exception as e:
    with open('db_info.txt', 'w') as f:
        f.write(f"Error: {e}\n")
