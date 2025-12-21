from sqlalchemy import text
from app.db.session import engine

def fix_ratings_table():
    # Adding created_at to movie_ratings table
    query = text("ALTER TABLE movie_ratings ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;")
    try:
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()
            print("Column 'created_at' added to movie_ratings successfully.")
    except Exception as e:
        print(f"Error updating table: {e}")

if __name__ == "__main__":
    fix_ratings_table()