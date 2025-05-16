import httpx
from fastapi import HTTPException
import logging

async def fetch_wx_articles(query: str):
    """获取微信公众号文章"""
    url = f"https://weixin.sogou.com/weixin?type=2&s_from=input&query={query}&ie=utf8&_sug_=n&_sug_type_="
    
    try:
        async with httpx.AsyncClient() as client:
            logging.info(f"正在请求URL: {url}")
            logging.debug(f"请求头")
            logging.warning(f"请求头")
            logging.error(f"请求头")
            logging.critical(f"请求头")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.text,
                "url": url
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")
