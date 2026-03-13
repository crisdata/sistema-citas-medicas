# Sistema Distribuido de Citas Médicas

## Sistemas Distribuidos — COTECNOVA
**Docente:** Jhon James Cano Sánchez

---

## Descripción general

Este sistema distribuido está compuesto por 6 microservicios independientes desarrollados con FastAPI, donde cada uno cumple una función específica dentro del flujo de gestión de citas médicas. Los servicios se comunican entre sí mediante peticiones HTTP y todos comparten la misma base de datos MySQL/MariaDB. Cada microservicio corre en su propio puerto, lo que permite que funcionen de forma aislada y a la vez coordinada dentro de la red.

---

## Microservicios del sistema

### Grupo 1 — Registro de Pacientes

- **Nombre:** Grupo 1 – Registro de Pacientes
- **Endpoint:** POST /pacientes
- **Parámetros (JSON body):** nombre (string), email (string, opcional)
- **Ejemplo request:**
```bash
curl -X POST http://192.168.1.57:8001/pacientes \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Ana García", "email": "ana@correo.com"}'
```
- **Ejemplo response:**
```json
{"id": 1, "nombre": "Ana García", "email": "ana@correo.com"}
```
- **IP y puerto:** 192.168.1.57:8001

---

### Grupo 2 — Consulta de Pacientes

- **Nombre:** Grupo 2 – Consulta de Pacientes
- **Endpoint:** GET /pacientes/{paciente_id}
- **Parámetros:** paciente_id (int) — se envía en la URL
- **Ejemplo request:**
```bash
curl http://192.168.1.57:8002/pacientes/1
```
- **Ejemplo response:**
```json
{"id": 1, "nombre": "Ana García", "email": "ana@correo.com"}
```
- **IP y puerto:** 192.168.1.57:8002

---

### Grupo 3 — Crear Citas

- **Nombre:** Grupo 3 – Crear Citas
- **Endpoint:** POST /citas
- **Parámetros (JSON body):** paciente_id (int), fecha (string YYYY-MM-DD HH:MM:SS), estado (string)
- **Ejemplo request:**
```bash
curl -X POST http://192.168.1.57:8003/citas \
  -H "Content-Type: application/json" \
  -d '{"paciente_id": 1, "fecha": "2026-06-15 10:00:00", "estado": "asignada"}'
```
- **Ejemplo response:**
```json
{"id": 1, "paciente_id": 1, "fecha": "2026-06-15 10:00:00", "estado": "asignada"}
```
- **IP y puerto:** 192.168.1.57:8003

---

### Grupo 4 — Consultar Citas

- **Nombre:** Grupo 4 – Consultar Citas
- **Endpoint:** GET /citas/{paciente_id}
- **Parámetros:** paciente_id (int) — se envía en la URL
- **Ejemplo request:**
```bash
curl http://192.168.1.57:8004/citas/1
```
- **Ejemplo response:**
```json
[{"id": 1, "paciente_id": 1, "fecha": "2026-06-15 10:00:00", "estado": "asignada"}]
```
- **IP y puerto:** 192.168.1.57:8004

---

### Grupo 5 — Cancelar Citas

- **Nombre:** Grupo 5 – Cancelar Citas
- **Endpoint:** DELETE /citas/{cita_id}
- **Parámetros:** cita_id (int) — se envía en la URL
- **Ejemplo request:**
```bash
curl -X DELETE http://192.168.1.57:8005/citas/1
```
- **Ejemplo response:**
```json
{"mensaje": "Cita id=1 cancelada exitosamente.", "cita": {"id": 1, "paciente_id": 1, "fecha": "2026-06-15 10:00:00", "estado": "cancelada"}}
```
- **IP y puerto:** 192.168.1.57:8005

---

### Grupo 6 — API Gateway

- **Nombre:** Grupo 6 – API Gateway
- **Endpoint:** POST /reservar-cita
- **Parámetros (JSON body):** paciente_id (int), fecha (string YYYY-MM-DD HH:MM:SS), estado (string)
- **Ejemplo request:**
```bash
curl -X POST http://192.168.1.57:8000/reservar-cita \
  -H "Content-Type: application/json" \
  -d '{"paciente_id": 1, "fecha": "2026-07-20 09:00:00", "estado": "asignada"}'
```
- **Ejemplo response:**
```json
{"mensaje": "Cita reservada exitosamente.", "paciente": {"id": 1, "nombre": "Ana García", "email": "ana@correo.com"}, "cita": {"id": 2, "paciente_id": 1, "fecha": "2026-07-20 09:00:00", "estado": "asignada"}}
```
- **IP y puerto:** 192.168.1.57:8000

---

## Estructura del repositorio

```
sistema-citas-medicas/
├── db/
│   └── citas_medicas.sql
├── grupo1_registro_pacientes/
│   └── main.py              ← POST /pacientes (puerto 8001)
├── grupo2_consulta_pacientes/
│   └── main.py              ← GET /pacientes/{id} (puerto 8002)
├── grupo3_crear_citas/
│   └── main.py              ← POST /citas (puerto 8003)
├── grupo4_consultar_citas/
│   └── main.py              ← GET /citas/{paciente_id} (puerto 8004)
├── grupo5_cancelar_citas/
│   └── main.py              ← DELETE /citas/{id} (puerto 8005)
├── grupo6_api_gateway/
│   └── main.py              ← POST /reservar-cita (puerto 8000)
├── .gitignore
└── README.md
```
