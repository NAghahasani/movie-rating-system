from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.controller.movie_controller import router as movie_router
from app.exceptions.handler import global_exception_handler, validation_exception_handler

app = FastAPI(title="Movie Rating System")

# ثبت هندلرهای اختصاصی برای خطاها
app.add_exception_handler(HTTPException, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# اضافه کردن روتر فیلم‌ها
app.include_router(movie_router)

# مخفی کردن این اندپوینت از لیست سواگر
@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to Movie Rating System API"}