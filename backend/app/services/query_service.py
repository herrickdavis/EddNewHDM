from sqlalchemy.orm import Session
from app.models import models
import pyodbc

import pandas as pd
import io
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

def run_query(db: Session, query_id: int, params: dict = {}):
    query = db.query(models.Query).filter(models.Query.id == query_id, models.Query.active == True).first()
    if not query:
        return {"error": "Query no encontrada"}
    datasource = db.query(models.Datasource).filter(models.Datasource.id == query.datasource_id).first()
    if not datasource:
        return {"error": "Datasource no encontrado"}

    conn = pyodbc.connect(datasource.conn_string)
    cursor = conn.cursor()

    sql = query.sql_text
    for key, value in params.items():
        placeholder = f":{key}"
        sql = sql.replace(placeholder, f"'{value}'")

    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    data = [dict(zip(columns, row)) for row in rows]
    conn.close()

    return {"columns": columns, "rows": data}

def test_datasource(conn_string: str):
    conn = pyodbc.connect(conn_string, timeout=5)
    conn.close()
    return {"ok": True}


def export_query(db, query_id: int, format: str = "xlsx"):
    result = run_query(db, query_id, params={})
    df = pd.DataFrame(result["rows"])

    buffer = io.BytesIO()

    if format == "xlsx":
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Resultados")
        buffer.seek(0)
        filename = "resultado.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    elif format == "csv":
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        filename = "resultado.csv"
        media_type = "text/csv"

    elif format == "txt":
        df.to_csv(buffer, index=False, sep="\t")
        buffer.seek(0)
        filename = "resultado.txt"
        media_type = "text/plain"

    elif format == "xml":
        xml_data = df.to_xml(index=False)
        buffer = io.BytesIO(xml_data.encode("utf-8"))
        filename = "resultado.xml"
        media_type = "application/xml"

    else:
        raise ValueError("Formato no soportado")

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
