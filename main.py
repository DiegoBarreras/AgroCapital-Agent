from fastapi import FastAPI
from lib.whatsapp.channel import app as whatsapp_app
import uvicorn
from config.config import settings

app = FastAPI(
    title="🌾 Agrocapital Agent",
    description="WhatsApp Channel + Agent System",
    version="1.0.0"
)

# Montar WhatsApp como sub-aplicación
app.mount("/whatsapp", whatsapp_app)

@app.get("/")
async def root():
    return {
        "service": "Agrocapital WhatsApp Agent",
        "status": "running",
        "whatsapp_endpoint": "/whatsapp/webhook/whatsapp",
        "health": "/whatsapp/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.FASTAPI_PORT,
        reload=settings.FASTAPI_DEBUG,
        log_level="info"
    )