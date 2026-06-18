import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Enum as SAEnum

from app.core.database import Base

# ── Enums ──────────────────────────────────────────────────────────────────


class TransactionStatus(PyEnum):
    pending_netting = "pending_netting"
    settled = "settled"
    absorbed = "absorbed"


class EventGroupStatus(PyEnum):
    open = "open"
    closed = "closed"


class AccountProvider(PyEnum):
    mercadopago = "mercadopago"
    invertironline = "invertironline"
    bank = "bank"
    manual = "manual"


class AccountType(PyEnum):
    checking = "checking"
    savings = "savings"
    investment = "investment"
    credit = "credit"


# ── Models ─────────────────────────────────────────────────────────────────


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    provider = Column(SAEnum(AccountProvider), nullable=False)
    type = Column(SAEnum(AccountType), nullable=False)
    name = Column(String(255), nullable=False, default="")
    credentials = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    transactions = relationship("Transaction", back_populates="account")


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    color = Column(String(7), nullable=False, default="#6366f1")
    icon = Column(String(64), nullable=False, default="tag")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    rules = relationship("CategorizationRule", back_populates="category")
    transactions = relationship("Transaction", back_populates="category")


class CategorizationRule(Base):
    __tablename__ = "categorization_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    keyword = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    category = relationship("Category", back_populates="rules")


class EventGroup(Base):
    __tablename__ = "event_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False, default="")
    status = Column(SAEnum(EventGroupStatus), nullable=False, default=EventGroupStatus.open)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    transactions = relationship("Transaction", back_populates="event_group")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    event_group_id = Column(UUID(as_uuid=True), ForeignKey("event_groups.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="ARS")
    description = Column(Text, nullable=False, default="")
    transaction_date = Column(DateTime, nullable=False)
    status = Column(SAEnum(TransactionStatus), nullable=False, default=TransactionStatus.settled)
    raw_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    account = relationship("Account", back_populates="transactions")
    event_group = relationship("EventGroup", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


class Envelope(Base):
    __tablename__ = "envelopes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    target_amount = Column(Numeric(14, 2), nullable=True)
    current_balance = Column(Numeric(14, 2), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
