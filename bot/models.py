from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    BigInteger, Integer, String, Numeric, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    base_currency: Mapped[str] = mapped_column(String(10), default="TJS", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="ru", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    categories: Mapped[List["Category"]] = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets: Mapped[List["Budget"]] = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    recurring_payments: Mapped[List["RecurringPayment"]] = relationship("RecurringPayment", back_populates="user", cascade="all, delete-orphan")
    learned_keywords: Mapped[List["LearnedKeyword"]] = relationship("LearnedKeyword", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'expense' or 'income'
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)  # List of keyword strings
    icon: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="categories")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="category")
    budgets: Mapped[List["Budget"]] = relationship("Budget", back_populates="category")
    recurring_payments: Mapped[List["RecurringPayment"]] = relationship("RecurringPayment", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    amount_base: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, default=1.0)
    raw_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'expense' or 'income'
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    category: Mapped["Category"] = relationship("Category", back_populates="transactions")

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="TJS")
    rate: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    monthly_limit: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="TJS")
    notify_at_percent: Mapped[int] = mapped_column(Integer, default=80, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="budgets")
    category: Mapped["Category"] = relationship("Category", back_populates="budgets")

class RecurringPayment(Base):
    __tablename__ = "recurring_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)  # 'daily', 'weekly', 'monthly'
    next_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="recurring_payments")
    category: Mapped["Category"] = relationship("Category", back_populates="recurring_payments")

class LearnedKeyword(Base):
    __tablename__ = "learned_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="learned_keywords")
    category: Mapped["Category"] = relationship("Category")
