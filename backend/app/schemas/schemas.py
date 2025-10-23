from pydantic import BaseModel
from typing import Optional, Any

class DatasourceBase(BaseModel):
    name: str
    engine: Optional[str] = "mssql"
    conn_string: str
    active: Optional[bool] = True

class DatasourceCreate(DatasourceBase): pass
class DatasourceOut(DatasourceBase):
    id: int
    class Config:
        from_attributes = True

class QueryBase(BaseModel):
    datasource_id: int
    name: str
    sql_text: str
    params_json: Optional[Any]
    schema_json: Optional[Any]
    rules_json: Optional[Any] = None  
    active: Optional[bool] = True


class QueryCreate(QueryBase): pass
class QueryOut(QueryBase):
    id: int
    class Config:
        from_attributes = True

class TemplateBase(BaseModel):
    name: str
    mode: Optional[str] = "horizontal"
    description: Optional[str]
    query_id: Optional[int]
    layout_json: Optional[Any]
    filters_json: Optional[Any]
    rules_json: Optional[Any]
    active: Optional[bool] = True

class TemplateCreate(TemplateBase): pass
class TemplateOut(TemplateBase):
    id: int
    class Config:
        from_attributes = True
