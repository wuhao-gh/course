import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from course import router as course_router
from homework import router as homework_router
from logger import (
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
    api_exception_handler,
    APIException
)
from practice import router as practice_router
from progress import router as progress_router
from qa import router as qa_router
from admin import router as admin_router
from auth import router as user_router

app = FastAPI(title="课程管理系统API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有路由
app.include_router(course_router)
app.include_router(homework_router)
app.include_router(practice_router)
app.include_router(progress_router)
app.include_router(qa_router)
app.include_router(admin_router)
app.include_router(user_router)
# app.include_router(stat_router)

# 注册异常处理器
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
