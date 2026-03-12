"""
Grupo 4 - Consultar Citas
Puerto: 8004
Endpoint: GET /citas/{paciente_id}
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import mysql.connector

# ── Configuración ────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "192.168.1.57"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER", "clase"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "database": os.getenv("DB_NAME", "citas_medicas"),
}

# ── Aplicación FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="Grupo 4 – Consultar Citas",
    description="Microservicio para consultar las citas médicas de un paciente.",
    version="1.0.0",
)


# ── Modelos ──────────────────────────────────────────────────────────────────
class CitaOut(BaseModel):
    id:             int
    paciente_id:    int
    fecha:          str
    estado:         str


# ── Utilidad ─────────────────────────────────────────────────────────────────
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health():
    return {"servicio": "Grupo 4 – Consultar Citas", "status": "ok", "puerto": 8004}


@app.get("/test-db", tags=["Health"])
def test_db():
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tablas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"status": "conectado", "tablas": tablas}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/citas", response_model=List[CitaOut], tags=["Citas"])
def listar_citas(estado: Optional[str] = None):
    """Lista todas las citas. Filtra por estado con ?estado=activa o ?estado=cancelada."""
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        if estado:
            cursor.execute("SELECT * FROM citas WHERE estado = %s ORDER BY fecha", (estado,))
        else:
            cursor.execute("SELECT * FROM citas ORDER BY fecha")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [
            {**r, "fecha": str(r["fecha"])}
            for r in rows
        ]
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.get("/citas/{paciente_id}", response_model=List[CitaOut], tags=["Citas"])
def consultar_citas_paciente(paciente_id: int, estado: Optional[str] = None):
    """
    Consulta todas las citas de un paciente.

    - **paciente_id**: ID del paciente  
    - **estado** (query param, opcional): `activa` | `cancelada`
    """
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        if estado:
            cursor.execute(
                "SELECT * FROM citas WHERE paciente_id = %s AND estado = %s ORDER BY fecha",
                (paciente_id, estado),
            )
        else:
            cursor.execute(
                "SELECT * FROM citas WHERE paciente_id = %s ORDER BY fecha",
                (paciente_id,),
            )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron citas para el paciente con id={paciente_id}.",
            )
        return [
            {**r, "fecha": str(r["fecha"])}
            for r in rows
        ]
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
