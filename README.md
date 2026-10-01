# Demo Avatar

Demo de generación de video con avatar usando FastAPI + frontend estático.

## Stack

- Python 3.12+
- FastAPI
- Uvicorn
- Requests
- python-dotenv
- Frontend HTML + Tailwind CDN

## Estructura

```text
demoavatar/
├── demo.html
├── README.md
├── .gitignore
├── back/
│   ├── .env
│   ├── .venv/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
```

## Requisitos

- Python 3.12 o superior
- Pip
- Una clave de API del servicio externo configurada en `back/.env`

## 1) Clonar / entrar al proyecto

```bash
cd /home/lander/Lander/chamba/demoavatar
```

## 2) Instalar dependencias del backend

```bash
cd back
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Configurar variables de entorno

Crea o edita `back/.env` con:

```env
HEYGEN_API_KEY=tu_api_key_aqui
```

También puedes usar este ejemplo:

```bash
cp .env.example .env
```

## 4) Ejecutar backend

```bash
cd back
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

La API quedará disponible en:

- http://localhost:8000
- http://localhost:8000/docs

## 5) Ejecutar frontend

Abre el archivo `demo.html` en el navegador o serve localmente:

```bash
cd ..
python3 -m http.server 8080
```

Luego visita:

- http://localhost:8080/demo.html

## Endpoints principales

### Crear avatar desde imagen

```bash
curl -X POST http://localhost:8000/api/create-avatar \
  -F "custom_image=@/ruta/a/tu/imagen.jpg"
```

### Generar video

```bash
curl -X POST http://localhost:8000/api/render-video \
  -F "campaign_key=acrilicos" \
  -F "voice_gender=female" \
  -F "preset_avatar_id=tu_avatar_id"
```

### Revisar estado del video

```bash
curl http://localhost:8000/api/video-status/tu_video_id
```

## Nota

Este proyecto está preparado para demo y pruebas rápidas. No es un servicio productivo completo ni una implementación con autenticación ni manejo de producción.

## Detección rápida de problemas

- Si aparece error de puerto ocupado: libera el proceso en el puerto 8000.
- Si aparece error de API key: revisa `back/.env`.
- Si falla la subida de imagen: revisa que el archivo sea una imagen válida.
- Si el frontend no se conecta: asegúrate de que el backend esté corriendo en localhost:8000.
