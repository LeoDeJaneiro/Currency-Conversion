"""Declare models and relationships."""
from sqlalchemy import Column, DateTime, Date, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import engine

Base = declarative_base()


class Rate(Base):
    """ Exchange rates of currencies related to a base currency. """

    __tablename__ = "rate"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    base_currency_id = Column(Integer, ForeignKey("base_currency.id"))
    date = Column(Date)
    # ... columns for each currency will be appended programtically. Naming by symbols: ["AED","AFN","ALL", ...]
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    base_currency = relationship("Base_currency")

    def __repr__(self):
        return "<Rate %r>" % self.id


class Base_currency(Base):
    """ Base currencies, such as USD & EUR. """

    __tablename__ = "base_currency"

    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    symbol = Column(String(3), index=True)
    name = Column(String)

    def __repr__(self):
        return "<Base_currency %r>" % self.symbol


Base.metadata.create_all(engine)
