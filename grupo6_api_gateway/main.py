"""
Grupo 6 - API Gateway
Puerto: 8000
Endpoint: POST /reservar-cita
Dependencias: Grupo 2 (GET /pacientes/{id}), Grupo 3 (POST /citas)
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import httpx

# ── Configuración de servicios internos ─────────────────────────────────────
# Reemplaza las IPs con las IPs reales de cada equipo en la red del aula
GRUPO1_URL = os.getenv("GRUPO1_URL", "http://127.0.0.1:8001")
GRUPO2_URL = os.getenv("GRUPO2_URL", "http://127.0.0.1:8002")
GRUPO3_URL = os.getenv("GRUPO3_URL", "http://127.0.0.1:8003")
GRUPO4_URL = os.getenv("GRUPO4_URL", "http://127.0.0.1:8004")
GRUPO5_URL = os.getenv("GRUPO5_URL", "http://127.0.0.1:8005")

# ── Aplicación FastAPI ───────────────────────────────────────────────────────
app = FastAPI(
    title="Grupo 6 – API Gateway",
    description=(
        "Punto de entrada unificado del sistema de citas médicas. "
        "Orquesta los microservicios de todos los grupos.\n\n"
        "| Servicio              | URL interna         |\n"
        "|----------------------|---------------------|\n"
        "| Grupo 1 – Registro   | /pacientes (POST)   |\n"
        "| Grupo 2 – Consulta   | /pacientes/{id}     |\n"
        "| Grupo 3 – Crear Cita | /citas (POST)       |\n"
        "| Grupo 4 – Ver Citas  | /citas/{id}         |\n"
        "| Grupo 5 – Cancelar   | /citas/{id} (DEL)   |\n"
    ),
    version="1.0.0",
)


# ── Modelos ──────────────────────────────────────────────────────────────────
class ReservaCitaIn(BaseModel):
    """Datos necesarios para reservar una cita a través del gateway."""
    paciente_id: int
    fecha:       str          # YYYY-MM-DD
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
    


class RegistrarYReservarIn(BaseModel):
    """Registra un paciente nuevo y le crea una cita en un solo paso."""
    nombre:   str
    email:    Optional[str] = None
    fecha:    str
    estado:   str

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre":   "Carlos Ruiz",
                "email":    "carlos@correo.com",
                "fecha":    "2026-03-20",
                "estado":   "asignada",
            }
        }
    }

class CitaOut(BaseModel):
    id:             int
    paciente_id:    int
    fecha:          str
    estado:         str

# ── Utilidad interna ─────────────────────────────────────────────────────────
def _call(method: str, url: str, **kwargs) -> dict:
    """Realiza una llamada HTTP a un microservicio y estandariza errores."""
    try:
        response = httpx.request(method, url, timeout=5.0, **kwargs)
        if response.status_code in (200, 201):
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.json())
    except HTTPException:
        raise
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Servicio no disponible: {url} — {e}")


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health():
    return {"servicio": "Grupo 6 – API Gateway", "status": "ok", "puerto": 8000}


@app.get("/estado-servicios", tags=["Health"])
def estado_servicios():
    """Verifica el estado de todos los microservicios del sistema."""
    servicios = {
        "grupo1_registro":   GRUPO1_URL,
        "grupo2_consulta":   GRUPO2_URL,
        "grupo3_crear_cita": GRUPO3_URL,
        "grupo4_ver_citas":  GRUPO4_URL,
        "grupo5_cancelar":   GRUPO5_URL,
    }
    resultado = {}
    for nombre, url in servicios.items():
        try:
            r = httpx.get(f"{url}/", timeout=3.0)
            resultado[nombre] = {"status": "ok" if r.status_code == 200 else "error", "url": url}
        except httpx.RequestError:
            resultado[nombre] = {"status": "no disponible", "url": url}
    return resultado


@app.post("/reservar-cita", status_code=201, tags=["Gateway"])
def reservar_cita(reserva: ReservaCitaIn):
    """
    **Flujo completo de reserva de cita** (paciente ya registrado):

    1. Verifica que el paciente exista → Grupo 2  
    2. Crea la cita → Grupo 3  
    3. Retorna la información consolidada  
    """
    # Paso 1: Verificar paciente (Grupo 2)
    paciente = _call("GET", f"{GRUPO2_URL}/pacientes/{reserva.paciente_id}")

    # Paso 2: Crear cita (Grupo 3)
    cita = _call("POST", f"{GRUPO3_URL}/citas", json={
        "paciente_id": reserva.paciente_id,
        "fecha":       reserva.fecha,
        "estado":      reserva.estado,
    })

    return {
        "mensaje":   "Cita reservada exitosamente.",
        "paciente":  paciente,
        "cita":      cita,
    }


@app.post("/registrar-y-reservar", status_code=201, tags=["Gateway"])
def registrar_y_reservar(datos: RegistrarYReservarIn):
    """
    **Flujo completo desde cero** (paciente nuevo):
    1. Registra el paciente → Grupo 1  
    2. Crea la cita → Grupo 3  
    3. Retorna la información consolidada  
    """
    # Paso 1: Registrar paciente (Grupo 1)
    paciente = _call("POST", f"{GRUPO1_URL}/pacientes", json={
        "nombre":   datos.nombre,
        "email":    datos.email,
    })

    # Paso 2: Crear cita (Grupo 3)
    cita = _call("POST", f"{GRUPO3_URL}/citas",  json={
        "paciente_id": paciente['id'],
        "fecha":       datos.fecha,
        "estado":      datos.estado,
    })

    return {
        "mensaje":   "Paciente registrado y cita creada exitosamente.",
        "paciente":  paciente,
        "cita":      cita,
    }


@app.get("/flujo-completo/{paciente_id}", tags=["Gateway"])
def flujo_consulta(paciente_id: int):
    """
    Consulta el estado completo de un paciente:
    información personal + todas sus citas.
    """
    # Datos del paciente (Grupo 2)
    paciente = _call("GET", f"{GRUPO2_URL}/pacientes/{paciente_id}")

    # Citas del paciente (Grupo 4)
    try:
        citas = _call("GET", f"{GRUPO4_URL}/citas/{paciente_id}")
    except HTTPException as e:
        citas = [] if e.status_code == 404 else (_ for _ in ()).throw(e)

    return {"paciente": paciente, "citas": citas}

@app.post("/cancelar-cita/{cita_id}", tags=["Gateway"])
def cancelar_cita(cita_id: int):
    cita = _call("DELETE", f"{GRUPO5_URL}/citas/{cita_id}")

    return {
        "mensaje":   cita['mensaje'],
    }


@app.get("/consultar-citas", response_model=List[CitaOut], tags=["Gateway"])
def listar_citas(estado: Optional[str] = None):

    # Citas del paciente (Grupo 4)
    try:
        citas = _call("GET", f"{GRUPO4_URL}/citas", params={"estado": estado} if estado else None)
    except HTTPException as e:
        citas = [] if e.status_code == 404 else (_ for _ in ()).throw(e)

    return [
        {**r, "fecha": str(r["fecha"])}
        for r in citas
    ]


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
