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
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from app.services.query_service import run_query
import json

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
    ds = db.query(models.Datasource).filter(
        models.Datasource.id == datasource_id).first()
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


# ✅ Exportar con reglas aplicadas (usa jsonlogic)
@router.post("/queries/run/{query_id}/export_filtered")
def export_query_filtered(query_id: int, format: str = "xlsx", db: Session = Depends(get_db)):

    from json_logic import jsonLogic

    # 1. Ejecutar la consulta normalmente
    result = run_query(db, query_id, params={})
    rows = result.get("rows", [])
    columns = result.get("columns", [])

    # 2. Buscar la regla
    query = db.query(models.Query).filter(models.Query.id == query_id).first()
    rule = getattr(query, "rules_json", None)

    # 3. Si hay regla, filtrar
    if rule:
        try:
            if isinstance(rule, str):
                rule = json.loads(rule)
            rows = [r for r in rows if jsonLogic(rule, r)]
        except Exception as e:
            print(f"Error aplicando regla JSONLogic: {e}")

    # 4. Exportar según formato
    df = pd.DataFrame(rows, columns=columns)
    buffer = io.BytesIO()

    if format == "xlsx":
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        filename = "resultado_filtrado.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == "csv":
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        filename = "resultado_filtrado.csv"
        media_type = "text/csv"
    else:
        df.to_csv(buffer, index=False, sep="\t")
        buffer.seek(0)
        filename = "resultado_filtrado.txt"
        media_type = "text/plain"

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ✅ Vista previa de una plantilla y su consulta asociada
# ✅ Vista previa de una plantilla y su consulta asociada (aplica layout_json)
@router.get("/templates/{template_id}/preview")
def preview_template(template_id: int, db: Session = Depends(get_db)):
    tpl = db.query(models.Template).filter(models.Template.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template no encontrado")

    q = db.query(models.Query).filter(models.Query.id == tpl.query_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Consulta asociada no encontrada")

    # Ejecutar la consulta original
    data = run_query(db, q.id, params={})
    rows = data.get("rows", [])
    columns = data.get("columns", [])

    # Aplicar layout_json si existe
    layout = getattr(tpl, "layout_json", None)
    selected_columns = []

    if layout and isinstance(layout, dict) and "columns" in layout:
        selected_columns = [col for col in layout["columns"] if col in columns]

        # Filtrar las columnas visibles
        filtered_rows = []
        for r in rows:
            filtered_row = {col: r[col] for col in selected_columns if col in r}
            filtered_rows.append(filtered_row)
        rows = filtered_rows
        columns = selected_columns

    return {
        "template": {
            "id": tpl.id,
            "name": tpl.name,
            "description": tpl.description,
            "mode": tpl.mode,
            "layout_json": tpl.layout_json,
        },
        "query": {"id": q.id, "name": q.name, "sql_text": q.sql_text},
        "data": {"columns": columns, "rows": rows},
    }
