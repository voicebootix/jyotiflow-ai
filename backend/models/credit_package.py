from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db import Base
import uuid

class CreditPackage(Base):
    __tablename__ = "credit_packages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    price_usd = Column(Numeric(10, 2), nullable=False)
    credits_amount = Column(Integer, nullable=False)
    bonus_credits = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 