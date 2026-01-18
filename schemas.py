"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ActionRequest(BaseModel):
    action: str


class ChatRequest(BaseModel):
    action: str
    message: str


class PurchaseRequest(BaseModel):
    item_name: str


class RentFlatRequest(BaseModel):
    tier: int


class EnrollCourseRequest(BaseModel):
    course_id: str


class ApplyJobRequest(BaseModel):
    job_title: str
