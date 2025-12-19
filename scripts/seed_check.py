from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


def verify_seeding():
    try:
        with Session(engine) as session:
            movie_count = session.execute(text("SELECT COUNT(*) FROM movies")).scalar_one()
            director_count = session.execute(text("SELECT COUNT(*) FROM directors")).scalar_one()
            rating_count = session.execute(text("SELECT COUNT(*) FROM movie_ratings")).scalar_one()

            print("--- Database Status ---")
            print(f"Movies: {movie_count}")
            print(f"Directors: {director_count}")
            print(f"Ratings: {rating_count}")

            if movie_count >= 1000:
                print("\nSUCCESS: Database is ready!")
            else:
                print("\nWARNING: Data missing.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    verify_seeding()