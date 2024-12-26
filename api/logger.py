import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FILE_HANDLER_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

def setup_logger(name: str, log_file: Optional[str] = None, level=logging.INFO) -> logging.Logger:
    """设置logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        file_handler = RotatingFileHandler(
            log_dir / log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(FILE_HANDLER_FORMAT))
        logger.addHandler(file_handler)

    return logger

# 设置根logger
root_logger = setup_logger("course_api", "app.log")

# 设置各模块logger
user_logger = setup_logger("course_api.user", "user.log")
course_logger = setup_logger("course_api.course", "course.log")
homework_logger = setup_logger("course_api.homework", "homework.log")
practice_logger = setup_logger("course_api.practice", "practice.log")
qa_logger = setup_logger("course_api.qa", "qa.log")
stat_logger = setup_logger("course_api.stat", "stat.log")

def log_error(logger: logging.Logger, error: Exception, request: Optional[Request] = None) -> Dict[str, Any]:
    """统一的错误日志记录"""
    error_detail = {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if request:
        error_detail.update({
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else None,
            "headers": dict(request.headers),
        })

    logger.error(
        f"Error occurred: {error_detail['error_type']} - {error_detail['error_message']}",
        extra=error_detail,
        exc_info=True
    )

    return error_detail

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证错误处理"""
    error_detail = log_error(root_logger, exc, request)
    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求参数验证失败",
            "errors": exc.errors(),
            **error_detail
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库错误处理"""
    error_detail = log_error(root_logger, exc, request)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "数据库操作失败",
            **error_detail
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """通用错误处理"""
    error_detail = log_error(root_logger, exc, request)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器内部错误",
            **error_detail
        }
    )

class APIException(Exception):
    """自定义API异常基类"""
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = None,
        data: Any = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.data = data
        super().__init__(message)

async def api_exception_handler(request: Request, exc: APIException):
    """自定义API异常处理"""
    error_detail = log_error(root_logger, exc, request)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "data": exc.data,
            **error_detail
        }
    )
