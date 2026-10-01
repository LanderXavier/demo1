import os
import requests
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="HeyGen Avatar Live Demo")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Backend funcionando"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
BASE_URL = "https://api.heygen.com"


async def upload_image_to_heygen(custom_image: UploadFile) -> str:
    upload_url = f"{BASE_URL}/v1/asset"
    file_bytes = await custom_image.read()
    files = {"file": (custom_image.filename, file_bytes, custom_image.content_type or "application/octet-stream")}
    headers_asset = {"X-Api-Key": HEYGEN_API_KEY}

    asset_res = requests.post(upload_url, headers=headers_asset, files=files, timeout=60)
    if asset_res.status_code != 200:
        raise HTTPException(status_code=asset_res.status_code, detail=f"Error subiendo imagen: {asset_res.text}")

    asset_data = asset_res.json().get("data", {})
    image_key = asset_data.get("image_key") or asset_data.get("id")
    if not image_key:
        raise HTTPException(status_code=400, detail="No se pudo obtener image_key de HeyGen")

    return image_key


async def register_talking_photo(image_key: str) -> str:
    tp_url = f"{BASE_URL}/v1/talking_photo"
    headers_json = {"X-Api-Key": HEYGEN_API_KEY, "Content-Type": "application/json"}
    tp_res = requests.post(tp_url, json={"image_key": image_key}, headers=headers_json, timeout=60)

    if tp_res.status_code != 200:
        raise HTTPException(status_code=tp_res.status_code, detail=f"Error registrando avatar: {tp_res.text}")

    talking_photo_id = tp_res.json().get("data", {}).get("talking_photo_id")
    if not talking_photo_id:
        raise HTTPException(status_code=400, detail="HeyGen no devolvió talking_photo_id")

    return talking_photo_id


# Diálogos predeterminados hardcodeados (15s cada uno)
CAMPAIGNS = {
    "acrilicos": "¡Atención chicas! Este jueves tus uñas se lucen al doble con nuestra promo dos por uno en acrílicas. Trae a tu mejor amiga y agenden su cita hoy mismo en el enlace del perfil.",
    "limpieza": "¡Luce una piel radiante! Por cualquier consumo superior a quince dólares en nuestros servicios, tu limpieza facial profunda va totalmente gratis. ¡Pide tu cita ahora!",
    "cocteles": "¡Corta la semana con todo! Este miércoles la casa invita: disfruta de nuestros cócteles soft completamente gratis con tus platillos favoritos. ¡Te esperamos hoy!"
}

# IDs de voces en español recomendadas (dicción neutra)
VOICES = {
    "female": "es-MX-DaliaNeural",
    "male": "es-MX-JorgeNeural"
}

@app.post("/api/create-avatar")
async def create_avatar(custom_image: UploadFile = File(...)):
    if not HEYGEN_API_KEY:
        raise HTTPException(status_code=500, detail="Falta HEYGEN_API_KEY en el entorno")

    if not custom_image or not custom_image.filename:
        raise HTTPException(status_code=400, detail="Debes subir una imagen")

    image_key = await upload_image_to_heygen(custom_image)
    talking_photo_id = await register_talking_photo(image_key)

    return {
        "status": "ready",
        "image_key": image_key,
        "talking_photo_id": talking_photo_id
    }


@app.post("/api/render-video")
async def render_video(
    campaign_key: str = Form(...),
    preset_avatar_id: str = Form(None),
    voice_gender: str = Form("female"),
    custom_image: UploadFile = File(None)
):
    if not HEYGEN_API_KEY:
        raise HTTPException(status_code=500, detail="Falta HEYGEN_API_KEY en el entorno")

    if campaign_key not in CAMPAIGNS:
        raise HTTPException(status_code=400, detail="Campaña no válida")

    script_text = CAMPAIGNS[campaign_key]
    voice_id = VOICES.get(voice_gender, VOICES["female"])
    talking_photo_id = preset_avatar_id

    if custom_image and custom_image.filename:
        image_key = await upload_image_to_heygen(custom_image)
        talking_photo_id = await register_talking_photo(image_key)

    if not talking_photo_id:
        raise HTTPException(status_code=400, detail="Debes seleccionar un avatar o subir una foto")

    gen_url = f"{BASE_URL}/v2/video/generate"
    headers_gen = {"X-Api-Key": HEYGEN_API_KEY, "Content-Type": "application/json"}

    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "talking_photo",
                    "talking_photo_id": talking_photo_id
                },
                "voice": {
                    "type": "text",
                    "input_text": script_text,
                    "voice_id": voice_id
                },
                "background": {
                    "type": "color",
                    "value": "#020617"
                }
            }
        ],
        "dimension": {
            "width": 1080,
            "height": 1920
        }
    }

    gen_res = requests.post(gen_url, json=payload, headers=headers_gen, timeout=60)
    if gen_res.status_code != 200:
        raise HTTPException(status_code=gen_res.status_code, detail=f"Error generando video: {gen_res.text}")

    video_id = gen_res.json().get("data", {}).get("video_id")
    return {"status": "processing", "video_id": video_id}

@app.get("/api/video-status/{video_id}")
def check_status(video_id: str):
    headers = {"X-Api-Key": HEYGEN_API_KEY}
    res = requests.get(f"{BASE_URL}/v1/video_status.get?video_id={video_id}", headers=headers)
    
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    data = res.json().get("data", {})
    return {
        "status": data.get("status"),       # 'processing', 'completed', 'failed'
        "video_url": data.get("video_url"),
        "error": data.get("error")
    }