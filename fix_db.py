from sqlalchemy import text
from app.db.session import engine

def add_updated_at_column():
    query = text("ALTER TABLE movies ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;")
    try:
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()
            print("ستون updated_at با موفقیت اضافه شد.")
    except Exception as e:
        print(f"خطا در به‌روزرسانی دیتابیس: {e}")

if __name__ == "__main__":
    add_updated_at_column()