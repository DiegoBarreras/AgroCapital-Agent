import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config:
    def __init__(self):
        # ==========================================
        # LLM PROVIDERS
        # ==========================================
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
        self.LLM_MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")

        # ==========================================
        # MEMORY
        # ==========================================
        self.MEM0_API_KEY = os.getenv("MEM0_API_KEY")

        # ==========================================
        # AWS
        # ==========================================
        self.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
        self.AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

        # ==========================================
        # TWILIO WHATSAPP
        # ==========================================
        self.TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
        self.TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
        self.TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

        # ==========================================
        # FASTAPI
        # ==========================================
        self.FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))
        self.FASTAPI_ENV = os.getenv("FASTAPI_ENV", "development")
        self.FASTAPI_DEBUG = os.getenv("FASTAPI_DEBUG", "true").lower() == "true"

        # ==========================================
        # AGENTE IA (Tu compañero 1-2)
        # ==========================================
        self.AGENT_API_URL = os.getenv("AGENT_API_URL", "http://localhost:8001")
        self.AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")

        # ==========================================
        # CRM (Tu compañero 3)
        # ==========================================
        self.CRM_API_URL = os.getenv("CRM_API_URL", "http://localhost:8002")
        self.CRM_API_KEY = os.getenv("CRM_API_KEY", "")

# Instancia global
settings = Config()