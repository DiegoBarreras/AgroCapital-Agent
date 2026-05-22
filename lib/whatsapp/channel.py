"""
FastAPI - Canal WhatsApp para Agrocapital
Recibe mensajes de Twilio, procesa, responde
"""

from fastapi import FastAPI, Request
from config.config import settings
from .twilio.twilio_service import TwilioService
import logging

logger = logging.getLogger(__name__)

# Crear app FastAPI para WhatsApp
app = FastAPI(title="WhatsApp Channel - Agrocapital")

# Inicializar servicio de Twilio
twilio_service = TwilioService()

# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
async def root():
    return {
        "service": "WhatsApp Channel",
        "status": "running",
        "twilio_number": settings.TWILIO_WHATSAPP_NUMBER,
        "webhook": "/webhook/whatsapp"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "whatsapp_channel",
        "twilio_connected": twilio_service.client is not None
    }

# ==========================================
# WEBHOOK - RECIBE MENSAJES DE TWILIO
# ==========================================

@app.post("/webhook/whatsapp")
async def webhook_whatsapp(request: Request):
    """
    🔑 ENDPOINT CRÍTICO
    
    Recibe mensajes de Twilio WhatsApp
    
    URL para Twilio Console:
    https://tu-ngrok-url.ngrok.io/whatsapp/webhook/whatsapp
    """
    
    try:
        # Obtener datos del formulario enviados por Twilio
        body = await request.form()
        
        # Extraer información del mensaje
        numero_usuario = body.get("From")      # whatsapp:+5215551234567
        texto_mensaje = body.get("Body", "")   # Texto del usuario
        message_sid = body.get("MessageSid")   # ID único del mensaje
        
        logger.info(f"📨 Mensaje recibido")
        logger.info(f"   De: {numero_usuario}")
        logger.info(f"   Texto: {texto_mensaje}")
        logger.info(f"   SID: {message_sid}")
        
        # ==========================================
        # PROCESAR MENSAJE
        # ==========================================
        # TODO: Aquí irá la lógica de:
        # 1. Obtener usuario del CRM
        # 2. Obtener historial
        # 3. Enviar al agente IA
        # 4. Guardar respuesta
        # Por ahora, solo respondemos echo
        
        respuesta_texto = f"Recibí tu mensaje: {texto_mensaje}"
        
        # ==========================================
        # ENVIAR RESPUESTA
        # ==========================================
        
        logger.info(f"💬 Enviando respuesta...")
        
        exito = twilio_service.send_whatsapp_message(
            to_number=numero_usuario,
            body=respuesta_texto
        )
        
        if exito:
            logger.info(f"✅ Respuesta enviada correctamente")
            return {
                "status": "success",
                "message_sid": message_sid,
                "response_sent": True
            }
        else:
            logger.error(f"❌ Error enviando respuesta")
            return {
                "status": "error",
                "message_sid": message_sid,
                "response_sent": False
            }
        
    except Exception as e:
        logger.error(f"❌ Error en webhook: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }