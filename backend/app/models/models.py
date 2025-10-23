from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from app.models.base import Base

class Datasource(Base):
    __tablename__ = "datasources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    engine = Column(String(20), default="mssql")
    conn_string = Column(Text, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True, index=True)
    datasource_id = Column(Integer, ForeignKey("datasources.id"))
    name = Column(String(200), nullable=False)
    sql_text = Column(Text, nullable=False)
    params_json = Column(JSON, nullable=True)
    schema_json = Column(JSON, nullable=True)
    rules_json = Column(JSON, nullable=True)  # ✅ ya soporta reglas JSONLogic
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    mode = Column(String(30), default="horizontal")
    description = Column(String(255), nullable=True)
    query_id = Column(Integer, ForeignKey("queries.id"))
    layout_json = Column(JSON, nullable=True)
    filters_json = Column(JSON, nullable=True)
    rules_json = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
