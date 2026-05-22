from fastapi import FastAPI, Request
from twilio.request_validator import RequestValidator
from config.config import settings
from lib.whatsapp.twilio.twilio_service import TwilioService
import logging

logger = logging.getLogger(__name__)

# Crear app FastAPI
app = FastAPI(title="WhatsApp Agrocapital")

# Inicializar Twilio
twilio_service = TwilioService()
validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)

@app.get("/")
async def root():
    return {"mensaje": "WhatsApp API funcionando"}

@app.post("/webhook/whatsapp")
async def webhook(request: Request):
    """
    Recibe mensajes de Twilio WhatsApp
    """
    
    # Obtener datos del formulario
    body = await request.form()
    
    # Extraer información
    numero_usuario = body.get("From")  # whatsapp:+5215551234567
    texto_mensaje = body.get("Body")   # "Hola quiero un crédito"
    message_sid = body.get("MessageSid")
    
    logger.info(f" Mensaje recibido de {numero_usuario}: {texto_mensaje}")
    
    try:
        # TODO: Aquí procesaremos el mensaje con el agente
        # Por ahora, solo respondemos
        
        respuesta = f"Recibí tu mensaje: {texto_mensaje}"
        
        # Enviar respuesta usando TwilioService
        twilio_service.send_whatsapp_message(
            to_number=numero_usuario,
            body=respuesta
        )
        
        logger.info(f"Respuesta enviada")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error"}