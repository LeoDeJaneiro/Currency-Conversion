from sqlalchemy import Column, UniqueConstraint, Date, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Exchange_rate(Base):
    """ Exchange rates of base to target currencies. """
    __tablename__ = "exchange_rate"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    base_currency_id = Column(Integer,
                              ForeignKey("base_currency.id"),
                              nullable=False)
    target_currency_id = Column(Integer,
                                ForeignKey("target_currency.id"),
                                nullable=False)
    rate = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    base_currency = relationship("Base_currency")
    target_currency = relationship("Target_currency")
    __table_args__ = (UniqueConstraint('base_currency_id',
                                       'target_currency_id',
                                       'date',
                                       name='rate_uc'), )

    def __repr__(self):
        return "<Exchange_rate %r>" % self.id


class Currency(object):
    """ Currency symbols and names """
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")
    symbol = Column(String(3), index=True, unique=True, nullable=False)
    name = Column(String)

    def __repr__(self):
        return "<Currency %r>" % self.symbol


class Base_currency(Currency, Base):
    """ Base currency symbols and names """
    __tablename__ = "base_currency"


class Target_currency(Currency, Base):
    """ Target currency symbols and names """
    __tablename__ = "target_currency"


def create_schema(engine):
    Base.metadata.create_all(engine)