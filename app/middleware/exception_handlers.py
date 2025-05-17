from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import ResponseValidationError
from app.schemas.common_data import ApiResponseData, PlatformEnum
from app.core.config import settings
# 自定义HTTP异常处理器
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    统一处理HTTP异常，转换为指定格式
    """
    print('http_exception_handler----exc----', exc)
    # 检查是否已包含自定义格式
    if isinstance(exc.detail, dict) and 'platform' in exc.detail and 'ret' in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # 获取路径信息
    path = request.url.path
    platform = "unknown"
    
    # 根据路径判断平台
    if "wx/public" in path:
        platform = "WX_PUBLIC"
    
    # 构建标准响应格式
    response_content = {
        'platform': platform,
        'ret': [f"ERROR::{exc.detail}"],
        'data': {
            "request_method": request.method,
        },
        'v': settings.VERSION,
        'api': path.strip("/")
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    ) 

# 自定义请求参数异常处理器
# 同时处理query参数和body参数的异常处理
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    """
    统一处理请求参数异常，转换为指定格式
    支持query参数和body参数的异常处理
    """
    print('request_validation_error_handler----exc----', exc)
    # 提示缺少哪个参数
    missing_fields = exc.errors()
    print('missing_fields----', missing_fields)
    
    # 处理不同类型的参数错误
    missing_field_names = []
    for error in missing_fields:
        # 检查错误位置类型
        if error['loc'][0] == 'query':
            # 查询参数错误
            missing_field_names.append(f"查询参数:{error['loc'][1]}")
        elif error['loc'][0] == 'body':
            # 请求体错误
            if len(error['loc']) > 1:
                # 如果是嵌套的body参数
                field_path = '.'.join(str(loc) for loc in error['loc'][1:])
                missing_field_names.append(f"请求体:{field_path}")
            else:
                missing_field_names.append("请求体")
        else:
            # 其他类型错误（如path, header等）
            if len(error['loc']) > 1:
                field_path = '.'.join(str(loc) for loc in error['loc'])
                missing_field_names.append(field_path)
            else:
                missing_field_names.append(error['loc'][0])
    
    missing_field_names_str = ', '.join(missing_field_names)
    print('missing_field_names_str----', missing_field_names_str)
    
    # 获取请求信息
    request_method = request.method
    request_url = request.url.path
    
    # 根据路径判断平台
    platform = "WX_MINI"
    if "wx/public" in request_url:
        platform = "WX_PUBLIC"
    
    return JSONResponse(
        status_code=422,
        content={
            "platform": platform,
            "ret": [f"ERROR::缺少必需的参数或参数格式错误: {missing_field_names_str}"],
            "data": {request_method: request_method},
            "v": settings.VERSION,
            "api": request_url.strip("/")
        }
    )


# 自定义响应格式验证异常处理器
async def response_validation_error_handler(request: Request, exc: ResponseValidationError):
    """
    统一处理响应格式验证异常，转换为指定格式
    1. 检查原始返回是字典还是其他类型
    2. 如果是字典，对比字典中的字段是否有符合定义要求的，有则覆盖，没有则提取
    3. 如果不是字典，则把对应的值放到指定格式的data字段中
    4. 其余字段自动补齐
    """
    
    # 获取请求信息
    request_method = request.method
    request_url = request.url.path
    original_response = exc.body
    
    # 根据路径判断平台
    platform = PlatformEnum.WX_PUBLIC if "wx/public" in request_url else "unknown"
    
    # 初始化标准响应格式
    formatted_response = {
        "platform": platform,
        "api": request_url.strip("/"),
        "ret": ["SUCCESS::请求成功"],
        "v": settings.VERSION
    }
    print('response_validation_error_handler----original_response----', original_response)
    # 检查原始响应是否为字典类型
    if isinstance(original_response, dict):
        # 检查字典中是否包含符合ApiResponseData模型要求的字段
        required_fields = ["platform", "api", "data", "ret", "v"]
        existing_fields = {}
        
        for field in required_fields:
            if field in original_response:
                # 如果原始响应中包含该字段，则保留
                existing_fields[field] = original_response[field]
        
        # 如果原始响应中包含所有必要字段，则直接使用原始响应中的data字段
        if "data" in existing_fields:
            data_content = {k: v for k, v in original_response.items() if k not in existing_fields}
            # 判断data_content字典是否为空
            if len(data_content) < 1:
                formatted_response["data"] = existing_fields["data"]
            else:
                formatted_response["data"] = {
                    "data": existing_fields["data"],
                    **data_content
                }
        else:
            # 否则，将整个原始响应作为data字段的值
            # 移除已经存在于formatted_response中的字段，避免重复
            data_content = {k: v for k, v in original_response.items() if k not in existing_fields}
            formatted_response["data"] = data_content
        
        # 使用原始响应中的其他字段覆盖formatted_response中的对应字段
        for field, value in existing_fields.items():
            if field != "data":  # data字段已经单独处理
                formatted_response[field] = value
    else:
        # 如果原始响应不是字典类型，直接将其放入data字段
        formatted_response["data"] = original_response
    
    return JSONResponse(
        status_code=200,  # 使用200状态码，因为这是一个有效的响应
        content=formatted_response
    )
