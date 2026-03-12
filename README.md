# Sistema Distribuido de Citas Médicas

## Sistemas Distribuidos — COTECNOVA
**Docente:** Jhon James Cano Sánchez

---

## Descripción general

Sistema distribuido compuesto por 6 microservicios independientes que se comunican entre sí mediante HTTP. Cada servicio corre en un puerto diferente dentro de la red del aula y todos comparten la misma base de datos MySQL/MariaDB.

---

## Microservicios del sistema

### Grupo 1 — Registro de pacientes

- **Endpoint:** POST /pacientes
- **Puerto:** 8001
- **Parámetros:** nombre (string), email (string)
- **Ejemplo request:**
```bash
curl -X POST http://192.168.1.57:8001/pacientes \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Ana García", "email": "ana@correo.com"}'
```
- **Ejemplo response:**
```json
{"mensaje": "Paciente registrado"}
```
- **IP del servicio:** (completar el día de la práctica)

---

### Grupo 2 — Consulta de pacientes

- **Endpoint:** GET /pacientes/{id}
- **Puerto:** 8002
- **Parámetros:** id (int) — se envía en la URL
- **Ejemplo request:**
```bash
curl http://192.168.1.57:8002/pacientes/1
```
- **Ejemplo response:**
```json
{"id": 1, "nombre": "Ana García", "email": "ana@correo.com"}
```
- **IP del servicio:** (completar el día de la práctica)

---

### Grupo 3 — Crear citas

- **Endpoint:** POST /citas
- **Puerto:** 8003
- **Parámetros:** paciente_id (int), fecha (string formato DATETIME)
- **Depende de:** Grupo 2 (consulta si el paciente existe antes de crear la cita)
- **Ejemplo request:**
```bash
curl -X POST http://192.168.1.57:8003/citas \
  -H "Content-Type: application/json" \
  -d '{"paciente_id": 1, "fecha": "2026-06-15 10:00:00"}'
```
- **Ejemplo response:**
```json
{"mensaje": "Cita creada"}
```
- **IP del servicio:** (completar el día de la práctica)

---

### Grupo 4 — Consultar citas

- **Endpoint:** GET /citas/{paciente_id}
- **Puerto:** 8004
- **Parámetros:** paciente_id (int) — se envía en la URL
- **Ejemplo request:**
```bash
curl http://192.168.1.57:8004/citas/1
```
- **Ejemplo response:**
```json
[
  {"id": 1, "paciente_id": 1, "fecha": "2026-06-15 10:00:00", "estado": "activa"}
]
```
- **IP del servicio:** (completar el día de la práctica)

---

### Grupo 5 — Cancelar citas

- **Endpoint:** DELETE /citas/{id}
- **Puerto:** 8005
- **Parámetros:** id (int) — se envía en la URL
- **Ejemplo request:**
```bash
curl -X DELETE http://192.168.1.57:8005/citas/1
```
- **Ejemplo response:**
```json
{"mensaje": "Cita cancelada"}
```
- **IP del servicio:** (completar el día de la práctica)

---

### Grupo 6 — API Gateway

- **Endpoint:** POST /reservar-cita
- **Puerto:** 8000
- **Parámetros:** paciente_id (int), fecha (string formato DATETIME)
- **Depende de:** Grupo 2 (consultar paciente) y Grupo 3 (crear cita)
- **Ejemplo request:**
```bash
curl -X POST http://192.168.1.57:8000/reservar-cita \
  -H "Content-Type: application/json" \
  -d '{"paciente_id": 1, "fecha": "2026-06-20 09:00:00"}'
```
- **Ejemplo response:**
```json
{"mensaje": "Cita creada"}
```
- **IP del servicio:** (completar el día de la práctica)

---

## Base de datos compartida

Todos los servicios se conectan a la misma base de datos MySQL/MariaDB. Un solo equipo la configura y los demás se conectan por la red.

**Datos de conexión:**
- **Host:** 172.29.212.254
- **Usuario:** clase
- **Contraseña:** 1234
- **Base de datos:** citas_medicas
- **Puerto:** 3306

**Script SQL:**
```sql
CREATE DATABASE citas_medicas;
USE citas_medicas;

CREATE TABLE pacientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  email VARCHAR(100)
);

CREATE TABLE citas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  paciente_id INT,
  fecha DATETIME,
  estado VARCHAR(20)
);
```

---

## Configuración del servidor de base de datos

1. Instalar MariaDB en WSL:
```bash
sudo apt update
sudo apt install mariadb-server -y
sudo service mysql start
```

2. Ejecutar el script SQL:
```bash
sudo mysql < setup.sql
```

3. Permitir conexiones externas editando la configuración:
```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```
Cambiar `bind-address = 127.0.0.1` por `bind-address = 0.0.0.0` y reiniciar:
```bash
sudo service mysql restart
```

4. Crear usuario de red:
```sql
CREATE USER 'clase'@'%' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON citas_medicas.* TO 'clase'@'%';
FLUSH PRIVILEGES;
```

5. Abrir puerto en Windows (PowerShell como administrador):
```powershell
New-NetFirewallRule -DisplayName "MySQL" -Direction Inbound -Protocol TCP -LocalPort 3306 -Action Allow
```

6. Verificar la IP del servidor:
```bash
ip a          # En WSL/Linux
ipconfig      # En Windows
```

---

## Ejecución de los microservicios

Cada grupo ejecuta su servicio así:
```bash
uvicorn main:app --host 0.0.0.0 --port PUERTO
```

El `0.0.0.0` permite que otros equipos de la red accedan al servicio.

| Grupo | Comando |
|-------|---------|
| 1 | `uvicorn main:app --host 0.0.0.0 --port 8001` |
| 2 | `uvicorn main:app --host 0.0.0.0 --port 8002` |
| 3 | `uvicorn main:app --host 0.0.0.0 --port 8003` |
| 4 | `uvicorn main:app --host 0.0.0.0 --port 8004` |
| 5 | `uvicorn main:app --host 0.0.0.0 --port 8005` |
| 6 | `uvicorn main:app --host 0.0.0.0 --port 8000` |

Cada servicio es accesible desde Swagger UI en: `http://IP_DEL_GRUPO:PUERTO/docs`

---

## Dependencias entre servicios

| Servicio | Debe consumir |
|----------|--------------|
| Crear cita (Grupo 3) | Consultar paciente (Grupo 2) |
| Consultar citas (Grupo 4) | Base de datos directamente |
| Cancelar cita (Grupo 5) | Base de datos directamente |
| API Gateway (Grupo 6) | Crear cita (Grupo 3) + Consultar paciente (Grupo 2) |

---

## Prueba de concurrencia

Abrir dos terminales al mismo tiempo y ejecutar en ambas:
```bash
curl -X POST http://172.29.212.254:8003/citas \
  -H "Content-Type: application/json" \
  -d '{"paciente_id": 1, "fecha": "2026-06-15 10:00:00"}'
```

**¿Qué ocurrió?** Se crearon dos citas para el mismo paciente en la misma fecha, generando un registro duplicado.

**¿Dónde está la sección crítica?** En el momento entre la verificación del paciente y el INSERT en la tabla citas. Si dos solicitudes pasan esa verificación al mismo tiempo, ambas insertan el registro sin saber que la otra ya lo hizo.

---

## Estructura del repositorio

```
sistema_citas/
├── db/
│   └── citas_medicas.sql
├── grupo1/
│   └── main.py        ← POST /pacientes (puerto 8001)
├── grupo2/
│   └── main.py        ← GET /pacientes/{id} (puerto 8002)
├── grupo3/
│   └── main.py        ← POST /citas (puerto 8003)
├── grupo4/
│   └── main.py        ← GET /citas/{paciente_id} (puerto 8004)
├── grupo5/
│   └── main.py        ← DELETE /citas/{id} (puerto 8005)
├── grupo6/
│   └── main.py        ← POST /reservar-cita (puerto 8000)
└── README.md
```

---

## Instalación de dependencias

```bash
pip install fastapi uvicorn mysql-connector-python requests
```
