from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.query_service import run_query, test_datasource
from fastapi.responses import FileResponse
from app.services.query_service import export_query
from fastapi import Request

from fastapi import APIRouter, Depends, Request

router = APIRouter()

@router.get("/datasources")
def get_datasources(db: Session = Depends(get_db)):
    return db.query(models.Datasource).all()

@router.post("/datasources")
def create_datasource(ds: schemas.DatasourceCreate, db: Session = Depends(get_db)):
    new_ds = models.Datasource(**ds.dict())
    db.add(new_ds)
    db.commit()
    db.refresh(new_ds)
    return new_ds

@router.post("/datasources/test")
def test_ds(body: dict):
    conn_string = body.get("conn_string")
    if not conn_string:
        raise HTTPException(status_code=400, detail="conn_string requerido")
    return test_datasource(conn_string)

@router.post("/datasources/test/{datasource_id}")
def test_ds_saved(datasource_id: int, db: Session = Depends(get_db)):
    ds = db.query(models.Datasource).filter(models.Datasource.id == datasource_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Datasource no encontrado")
    return test_datasource(ds.conn_string)

@router.get("/queries")
def get_queries(db: Session = Depends(get_db)):
    return db.query(models.Query).all()

@router.post("/queries")
def create_query(q: schemas.QueryCreate, db: Session = Depends(get_db)):
    new_q = models.Query(**q.dict())
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return new_q

@router.post("/queries/run/{query_id}")
async def execute_query(query_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        # Si el frontend no envía body, evita error 422
        body = await request.json() if request.method == "POST" else {}
    except Exception:
        body = {}
    params = body if isinstance(body, dict) else {}
    return run_query(db, query_id, params)

@router.get("/templates")
def get_templates(db: Session = Depends(get_db)):
    return db.query(models.Template).all()

@router.post("/templates")
def create_template(t: schemas.TemplateCreate, db: Session = Depends(get_db)):
    new_t = models.Template(**t.dict())
    db.add(new_t)
    db.commit()
    db.refresh(new_t)
    return new_t


@router.post("/queries/run/{query_id}/export")
def export_query_route(query_id: int, format: str = "xlsx", db: Session = Depends(get_db)):
    try:
        return export_query(db, query_id, format)
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/queries/{query_id}")
def get_query(query_id: int, db: Session = Depends(get_db)):
    q = db.query(models.Query).filter(models.Query.id == query_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Query no encontrada")
    return q
