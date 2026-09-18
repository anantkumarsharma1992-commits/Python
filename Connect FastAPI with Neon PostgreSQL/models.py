"""
models.py

Pydantic models, following the exact same StudentCreate pattern your
instructor built live in class (from_pydantic import BaseModel, EmailStr).

Two additions beyond what class covered, both needed for today's task:
- *Update models (StudentUpdate, CourseUpdate, EnrollmentUpdate) - your
  class only ever updated ONE field (city) directly via a query parameter,
  with no Pydantic model at all. Today's task asks for general "updating
  records", so these models generalize that into a proper PATCH body -
  every field Optional, with an explicit default=None so exclude_unset
  works correctly (the exact fix from an earlier debugging session).
- CourseCreate / EnrollmentCreate - your class's code only ever built the
  Studentcreate model; these follow the identical shape for the other
  two tables.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    age: int
    city: str


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    city: Optional[str] = None


class CourseCreate(BaseModel):
    title: str
    instructor: str
    price: float
    duration: float


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    instructor: Optional[str] = None
    price: Optional[float] = None
    duration: Optional[float] = None


class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentUpdate(BaseModel):
    status: Optional[str] = Field(default=None, pattern="^(active|completed|cancelled)$")
