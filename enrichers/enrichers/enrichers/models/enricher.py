"""Submodule providing enrichers models."""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from alchemy_wrapper.models.base import Base


class Enricher(Base):
    """Define the Enricher model."""

    __tablename__ = "enrichers"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    last_ping_time = Column(DateTime, nullable=True, default=func.now())

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Enricher({self.name!r})>"

    def ping(self):
        """Ping the enricher."""
        self.last_ping_time = func.now()