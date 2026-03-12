"""
Grupo 3 - Crear Citas
Puerto: 8003
Endpoint: POST /citas
Dependencia: Consulta primero Grupo 2 (GET /pacientes/{id}) para validar que el paciente existe.
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import mysql.connector
import httpx

# ── Configuración ────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "192.168.1.57"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER", "clase"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "database": os.getenv("DB_NAME", "citas_medicas"),
}

# URL del servicio Grupo 2 (Consulta de Pacientes)
GRUPO2_URL = os.getenv("GRUPO2_URL", "http://127.0.0.1:8002")

# ── Aplicación FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="Grupo 3 – Crear Citas",
    description=(
        "Microservicio para crear nuevas citas médicas. "
        "**Consume Grupo 2** para verificar que el paciente exista antes de crear la cita."
    ),
    version="1.0.0",
)


# ── Modelos ──────────────────────────────────────────────────────────────────
class CitaIn(BaseModel):
    paciente_id: int
    fecha:       str          # formato: YYYY-MM-DD
    estado:      str

    model_config = {
        "json_schema_extra": {
            "example": {
                "paciente_id": 1,
                "fecha":       "2026-03-20" " " "02:02:30",
                "estado":      "asignada",
            }
        }
    }


class CitaOut(BaseModel):
    id:             int
    paciente_id:    int
    fecha:          str
    estado:         str


# ── Utilidad ─────────────────────────────────────────────────────────────────
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


def verificar_paciente(paciente_id: int) -> dict:
    """
    Llama al Grupo 2 para verificar que el paciente exista.
    Lanza HTTPException 404 si no existe, 503 si el servicio no está disponible.
    """
    try:
        response = httpx.get(f"{GRUPO2_URL}/pacientes/{paciente_id}", timeout=5.0)
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con id={paciente_id} no existe. Registrarlo primero en Grupo 1.",
            )
        response.raise_for_status()
        return response.json()
    except HTTPException:
        raise
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail=f"Servicio Grupo 2 no disponible en {GRUPO2_URL}. Verifica que esté corriendo.",
        )


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health():
    return {"servicio": "Grupo 3 – Crear Citas", "status": "ok", "puerto": 8003}


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


@app.post("/citas", response_model=CitaOut, status_code=201, tags=["Citas"])
def crear_cita(cita: CitaIn):
    """
    Crea una nueva cita médica.

    **Flujo interno:**
    1. Verifica que el paciente exista consultando Grupo 2.
    2. Inserta la cita en la base de datos.

    - **paciente_id**: ID del paciente (debe existir en el sistema)
    - **fecha**: Fecha de la cita en formato `YYYY-MM-DD` `hh:mi:ss`
    - **estado**: Estado de la consulta (Asignada)
    """
    # PASO 1: Verificar que el paciente existe (consume Grupo 2)
    verificar_paciente(cita.paciente_id)

    # PASO 2: Insertar la cita
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """INSERT INTO citas (paciente_id, fecha, estado)
               VALUES (%s, %s, %s)""",
            (cita.paciente_id, cita.fecha, cita.estado),
        )
        conn.commit()
        nueva_id = cursor.lastrowid
        cursor.execute("SELECT * FROM citas WHERE id = %s", (nueva_id,))
        nueva = cursor.fetchone()
        cursor.close()
        conn.close()
        return {
            **nueva,
            "fecha":          str(nueva["fecha"]),
            "estado": str(nueva["estado"]),
        }
    except mysql.connector.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe una cita para el paciente {cita.paciente_id} el {cita.fecha}.",
        )
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
