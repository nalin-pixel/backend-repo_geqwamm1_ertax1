"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List

# ---- Blog Post ----
class Post(BaseModel):
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Markdown or plain text content")
    author: str = Field(..., description="Author name")
    cover_image: Optional[HttpUrl] = Field(None, description="Optional cover image URL")
    tags: List[str] = Field(default_factory=list, description="Tags for the post")

# ---- Resource Links ----
class Resource(BaseModel):
    title: str = Field(..., description="Resource title")
    description: Optional[str] = Field(None, description="Short description")
    url: HttpUrl = Field(..., description="External link")
    category: Optional[str] = Field(None, description="Category or topic")

# ---- Doctors Catalog ----
class Doctor(BaseModel):
    name: str = Field(..., description="Full name of the doctor")
    specialty: str = Field(..., description="Medical specialty")
    bio: Optional[str] = Field(None, description="Short biography")
    photo_url: Optional[HttpUrl] = Field(None, description="Photo URL")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Star rating (set only when creating)")
    clinic: Optional[str] = Field(None, description="Clinic or hospital")
    location: Optional[str] = Field(None, description="City, Country")

# ---- Contact Messages ----
class Message(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
