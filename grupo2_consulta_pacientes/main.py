"""
Grupo 2 - Consulta de Pacientes
Puerto: 8002
Endpoint: GET /pacientes/{id}
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import mysql.connector

# ── Configuración de base de datos ──────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "192.168.1.57"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER", "clase"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "database": os.getenv("DB_NAME", "citas_medicas"),
}

# ── Aplicación FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="Grupo 2 – Consulta de Pacientes",
    description="Microservicio para consultar información de pacientes registrados.",
    version="1.0.0",
)


# ── Modelos ──────────────────────────────────────────────────────────────────
class PacienteOut(BaseModel):
    id:             int
    nombre:         str
    email:          Optional[str]


# ── Utilidad ─────────────────────────────────────────────────────────────────
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health():
    """Verifica que el servicio esté activo."""
    return {"servicio": "Grupo 2 – Consulta de Pacientes", "status": "ok", "puerto": 8002}


@app.get("/test-db", tags=["Health"])
def test_db():
    """Verifica la conexión a la base de datos compartida."""
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


@app.get("/pacientes", response_model=List[PacienteOut], tags=["Pacientes"])
def listar_pacientes():
    """Lista todos los pacientes registrados."""
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes ORDER BY id")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{**r} for r in rows]
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


@app.get("/pacientes/{paciente_id}", response_model=PacienteOut, tags=["Pacientes"])
def consultar_paciente(paciente_id: int):
    """
    Consulta la información de un paciente por su ID.

    - **paciente_id**: ID numérico del paciente
    """
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pacientes WHERE id = %s", (paciente_id,))
        paciente = cursor.fetchone()
        cursor.close()
        conn.close()
        if not paciente:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con id={paciente_id} no encontrado.",
            )
        return {**paciente}
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
