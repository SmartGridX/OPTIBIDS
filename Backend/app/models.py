# backend/app/models.py
from sqlmodel import SQLModel, Field, Text
from typing import Optional
from datetime import datetime
from sqlmodel import  Field, Relationship
from typing import Optional, List

# -------------------------------------------
# USER MODEL
# -------------------------------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str   # NOT NULL
    role: str = Field(default="applicant")

    applications: list["Application"] = Relationship(back_populates="user")


# -------------------------------------------
# TENDER MODEL
# -------------------------------------------
class Tender(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    description: str
    raw_text: str
    summary_json: Optional[str] = None
    status: str = "draft"
    files: Optional[str] = None

    applications: List["Application"] = Relationship()
# -------------------------------------------
# APPLICATION MODEL
# -------------------------------------------
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    tender_id: int = Field(foreign_key="tender.id")
    user_id: int = Field(foreign_key="user.id")

    applicant_text: str

    status: str = Field(default="submitted", index=True)
    offer_json: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="applications")




class Requirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tender_id: int
    req_json: str
    confidence: float

class SKU(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku_code: str
    description: str
    specs_json: Optional[str] = None
    price_base: float = 0.0

class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tender_id: int
    sku_id: int
    score: float
    explanation: Optional[str] = None

class Pricing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tender_id: int
    line_items: str
    total_amount: float
    margin_percent: float = 10.0
