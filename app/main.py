from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.api import api_router
from app.db.sqlalchemy_db import database
from fastapi.exceptions import RequestValidationError, HTTPException
from app.middleware.exception_handlers import request_validation_error_handler, http_exception_handler

# 初始化日志系统
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义全局请求参数异常处理器exception_class : 要处理的异常类型、handler : 处理异常的函数
app.add_exception_handler(RequestValidationError, request_validation_error_handler)

# 定义全局错误处理器，单独封装成一个中间价，并且统一返回相同的格式
app.add_exception_handler(HTTPException, http_exception_handler)

# 添加路由
app.include_router(api_router, prefix=settings.API_PREFIX)

# 创建数据库连接池
print('database.connect()3')
database.connect()

@app.get("/")
async def root():
    return {"message": "微信公众号爬虫API"}

if __name__ == "__main__":
    import uvicorn
    logging.info("启动应用服务器...")
    uvicorn.run("app.main:app", host="localhost", port=8002, reload=True)
