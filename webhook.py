"""
Webhook FastAPI para AgroAssistant.
Recibe mensajes de WhatsApp via Twilio y los procesa con el agente.

Ejecución:
    uv run python webhook.py
"""

import asyncio
import os
import sys
import uuid

from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse
import uvicorn

from config.config import settings
from core.engine import create_deep_agent, run_agent
from prompts.agrocapital import AGROCAPITAL_AGENT_PROMPT
from tools import ALL_TOOLS

sys.stdin.reconfigure(encoding='utf-8', errors='replace')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

app = FastAPI(title="AgroAssistant Webhook")

# Sesiones activas por número de teléfono
# { "+5216681234567": {"agent": ..., "conn": ..., "thread_id": ...} }
_sesiones = {}
_agente_global = None
_conn_global = None


async def obtener_agente():
    """Inicializa el agente una sola vez al arrancar."""
    global _agente_global, _conn_global
    if _agente_global is None:
        print("Inicializando AgroAssistant...")
        _agente_global, _conn_global = await create_deep_agent(
            system_prompt=AGROCAPITAL_AGENT_PROMPT,
            tools=ALL_TOOLS,
            provider=settings.LLM_PROVIDER,
            model_name=settings.LLM_MODEL,
            db_path="./agrocapital_webhook.db",
        )
        print("AgroAssistant listo.")
    return _agente_global


@app.on_event("startup")
async def startup():
    await obtener_agente()


@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(
    From: str = Form(...),
    Body: str = Form(...),
):
    """
    Recibe mensajes de WhatsApp desde Twilio y responde con el agente.
    Twilio espera una respuesta TwiML con el mensaje de vuelta.
    """
    numero = From.replace("whatsapp:", "")
    mensaje = Body.strip()

    print(f"\n[{numero}]: {mensaje}")

    # Obtener o crear thread_id para esta sesión
    if numero not in _sesiones:
        _sesiones[numero] = str(uuid.uuid4())
        print(f"Nueva sesión para {numero}: {_sesiones[numero][:8]}...")

    thread_id = _sesiones[numero]

    try:
        agente = await obtener_agente()
        respuesta = await run_agent(
            agent=agente,
            task=mensaje,
            thread_id=thread_id,
        )
        print(f"[AgroAssistant -> {numero}]: {respuesta[:100]}...")

    except Exception as e:
        respuesta = "Lo siento, tuve un problema procesando tu mensaje. Por favor intenta de nuevo."
        print(f"[Error]: {str(e)}")

    # Respuesta TwiML para Twilio
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{respuesta}</Message>
</Response>"""

    return PlainTextResponse(content=twiml, media_type="application/xml")


@app.get("/")
async def health():
    return {"status": "AgroAssistant activo", "modelo": settings.LLM_MODEL}


if __name__ == "__main__":
    if (
        not settings.OPENAI_API_KEY
        and not settings.GEMINI_API_KEY
        and not settings.ANTHROPIC_API_KEY
    ):
        print("Error: No se detectó ninguna API Key de LLM en .env")
        sys.exit(1)

    print("=" * 68)
    print("  AGROASSISTANT WEBHOOK — AgroCapital del Noroeste")
    print("=" * 68)
    print("  Servidor: http://localhost:8000")
    print("  Webhook:  http://localhost:8000/webhook")
    print("=" * 68)

    uvicorn.run(app, host="0.0.0.0", port=8000)