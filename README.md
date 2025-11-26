# Guía rápida para levantar y probar Back-CINiad

## Requisitos
- Python 3.12 (con `venv` y `pip` disponibles). Si tu sistema no trae `pip` en el venv, instala el paquete del sistema `python3-venv` / `python3-pip` o usa `get-pip.py`.

## Paso a paso
1) Ubícate en la carpeta `Back-CINiad`.
2) (Opcional pero recomendado) Crear y activar entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows PowerShell: venv\Scripts\Activate.ps1
   ```
3) Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4) Ejecuta el servidor:
   ```bash
   uvicorn main:app --reload
   ```
   Servirá la API en `http://127.0.0.1:8000` y los archivos subidos en `http://127.0.0.1:8000/media`.

## Rutas principales (para todas las tablas)
Tablas: `terapias`, `programas`, `talleres`, `actividades`, `recursos`.

- `POST /{tabla}` — Crea registro. Cuerpo `multipart/form-data` con:
  - `nombre` (texto, requerido)
  - `descripcion` (texto, opcional)
  - `file` (archivo imagen/video opcional; si envías otro tipo, fallará)
- `GET /{tabla}` — Lista todos.
- `GET /{tabla}/{id}` — Obtiene uno.
- `PUT /{tabla}/{id}` — Actualiza; si envías `file`, reemplaza el anterior y borra el viejo archivo.
- `DELETE /{tabla}/{id}` — Elimina registro y su archivo asociado.

`media_url` apunta a la versión normal (WebP, máx 1600px) y `media_card_url` a la versión reducida para cards (WebP, máx 480px). Se consumen desde `/media/<archivo>`.

## Ejemplos rápidos con curl
```bash
# Crear terapia
curl -X POST http://127.0.0.1:8000/terapias \
  -F "nombre=Terapia demo" \
  -F "descripcion=Algo" \
  -F "file=@/ruta/a/imagen.jpg"

# Listar talleres
curl http://127.0.0.1:8000/talleres

# Actualizar actividad (cambiando archivo)
curl -X PUT http://127.0.0.1:8000/actividades/1 \
  -F "nombre=Actividad nueva" \
  -F "descripcion=Texto" \
  -F "file=@/ruta/a/video.mp4"

# Eliminar recurso
curl -X DELETE http://127.0.0.1:8000/recursos/1
```

## Notas
- CORS está abierto (`*`) para facilitar integración con cualquier frontend.
- En producción, cambia `DATABASE_URL` en `main.py` a Postgres y sirve `/media` con Nginx/CDN.
- Tamaño y tipo de archivo se validan por extensión; añade validaciones extra si lo necesitas.***

## Autenticación (JWT)
- Endpoints nuevos:
  - `POST /auth/register` con cuerpo JSON `{"username": "...", "password": "..."}`.
  - `POST /auth/login` (form-data u `application/x-www-form-urlencoded`) con `username` y `password` devuelve `access_token` tipo Bearer.
- Solo usuarios autenticados pueden hacer `POST`, `PUT` o `DELETE` en las tablas; `GET` sigue abierto.
- Usa el header `Authorization: Bearer <token>` en las peticiones protegidas.
- Ejemplo rápido:
  ```bash
  # Registrar
  curl -X POST http://127.0.0.1:8000/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"123456"}'

  # Login
  TOKEN=$(curl -X POST http://127.0.0.1:8000/auth/login -d "username=admin&password=123456" -d "grant_type=" | jq -r .access_token)

  # Crear recurso protegido
  curl -X POST http://127.0.0.1:8000/terapias \
    -H "Authorization: Bearer $TOKEN" \
    -F "nombre=Terapia segura"
  ```
