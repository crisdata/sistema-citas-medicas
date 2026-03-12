"""
Grupo 1 - Registro de Pacientes
Puerto: 8001
Endpoint: POST /pacientes
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import mysql.connector

# ── Configuración de base de datos ──────────────────────────────────────────
# Cambia DB_HOST por la IP del equipo servidor de la clase
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "192.168.1.57"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER", "clase"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "database": os.getenv("DB_NAME", "citas_medicas"),
}

# ── Aplicación FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="Grupo 1 – Registro de Pacientes",
    description="Microservicio para registrar nuevos pacientes en el sistema de citas médicas.",
    version="1.0.0",
)


# ── Modelos ──────────────────────────────────────────────────────────────────
class PacienteIn(BaseModel):
    nombre:   str
    email:    Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre":   "Ana García",
                "email":    "ana@correo.com",
            }
        }
    }


class PacienteOut(BaseModel):
    id:              int
    nombre:          str
    email:           Optional[str]


# ── Utilidad ─────────────────────────────────────────────────────────────────
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health():
    """Verifica que el servicio esté activo."""
    return {"servicio": "Grupo 1 – Registro de Pacientes", "status": "ok", "puerto": 8001}


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


@app.post("/pacientes", response_model=PacienteOut, status_code=201, tags=["Pacientes"])
def registrar_paciente(paciente: PacienteIn):
    """
    Registra un nuevo paciente.

    - **nombre**: Nombre completo del paciente 
    - **email**: Correo electrónico (opcional)  
    """
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO pacientes (nombre, email) VALUES (%s, %s)",
            (paciente.nombre, paciente.email),
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.execute("SELECT * FROM pacientes WHERE id = %s", (nuevo_id,))
        nuevo = cursor.fetchone()
        cursor.close()
        conn.close()
        return {**nuevo}
    except mysql.connector.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un paciente con cédula '{paciente.cedula}'.",
        )
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
