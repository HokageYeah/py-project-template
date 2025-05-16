from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ArticleBase(BaseModel):
    title: str
    author: Optional[str] = None
    public_account: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    publish_date: Optional[str] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(ArticleBase):
    title: Optional[str] = None


class ArticleInDBBase(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Article(ArticleInDBBase):
    pass
