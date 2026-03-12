"""
Grupo 5 - Cancelar Citas
Puerto: 8005
Endpoint: DELETE /citas/{id}
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
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
    title="Grupo 5 – Cancelar Citas",
    description="Microservicio para cancelar citas médicas activas.",
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
    return {"servicio": "Grupo 5 – Cancelar Citas", "status": "ok", "puerto": 8005}


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


@app.delete("/citas/{cita_id}", tags=["Citas"])
def cancelar_cita(cita_id: int):
    """
    Cancela una cita médica activa (cambia su estado a `cancelada`).

    No elimina el registro físicamente: preserva el historial.

    - **cita_id**: ID de la cita a cancelar
    """
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        # Verificar existencia de la cita
        cursor.execute("SELECT * FROM citas WHERE id = %s", (cita_id,))
        cita = cursor.fetchone()
        if not cita:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Cita con id={cita_id} no encontrada.")

        if cita["estado"] == "cancelada":
            cursor.close()
            conn.close()
            raise HTTPException(status_code=409, detail=f"La cita con id={cita_id} ya está cancelada.")

        # Cancelar la cita (soft delete)
        cursor.execute("UPDATE citas SET estado = 'cancelada' WHERE id = %s", (cita_id,))
        conn.commit()

        # Retornar el estado actualizado
        cursor.execute("SELECT * FROM citas WHERE id = %s", (cita_id,))
        actualizada = cursor.fetchone()
        cursor.close()
        conn.close()

        return {
            "mensaje":  f"Cita id={cita_id} cancelada exitosamente.",
            "cita": {
                **actualizada,
                "fecha":          str(actualizada["fecha"]),
            },
        }
    except HTTPException:
        raise
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {e}")


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
