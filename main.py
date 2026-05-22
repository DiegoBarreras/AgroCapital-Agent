"""
AgroBot - Agente Inteligente de Crédito Agrícola
AgroCapital del Noroeste, S.A. de C.V., SOFOM E.N.R.

Flujo del agente:
    1. Productor interactúa por consola (o WhatsApp en producción)
    2. Agente evalúa viabilidad crediticia con ML (score_lead)
    3. Verifica requisitos documentales FIRA (verificar_requisitos_fira)
    4. Notifica resultados por WhatsApp
    5. Gestiona documentos en AWS S3

Ejecución:
    uv run python main.py
"""

import asyncio
import os
import sys
import uuid

from config.config import settings
from core.engine import create_deep_agent, run_agent
from prompts.agrocapital import AGROCAPITAL_AGENT_PROMPT
from tools import ALL_TOOLS


async def iniciar_agente(db_path: str = "./agrocapital_checkpoints.db"):
    """
    Inicializa AgroBot y abre una sesión conversacional interactiva
    con un productor agrícola.
    """
    # Cada sesión tiene su propio thread_id para mantener historial separado
    thread_id = str(uuid.uuid4())

    print("=" * 68)
    print("  AGROBOT — Agente de Crédito Agrícola | AgroCapital del Noroeste")
    print("=" * 68)
    print(f"  Sesión iniciada: {thread_id[:8]}...")
    print(f"  Modelo         : {settings.LLM_PROVIDER} / {settings.LLM_MODEL}")
    print("-" * 68)
    print("  Escribe 'salir' para terminar la sesión.")
    print("=" * 68)
    print()

    # Compilar el agente con todas las herramientas
    print("Iniciando AgroBot...")
    agent, db_conn = await create_deep_agent(
        system_prompt=AGROCAPITAL_AGENT_PROMPT,
        tools=ALL_TOOLS,
        provider=settings.LLM_PROVIDER,
        model_name=settings.LLM_MODEL,
        db_path=db_path,
    )
    print("AgroBot listo.\n")

    try:
        while True:
            # Leer entrada del productor
            try:
                entrada = input("Productor: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nSesión finalizada.")
                break

            if not entrada:
                continue

            if entrada.lower() in ["salir", "exit", "quit"]:
                print("\nHasta luego. AgroCapital le desea éxito en su ciclo productivo.")
                break

            # Enviar mensaje al agente y obtener respuesta
            try:
                respuesta = await run_agent(
                    agent=agent,
                    task=entrada,
                    thread_id=thread_id,
                )
                print(f"\nAgroBot: {respuesta}\n")
            except Exception as e:
                print(f"\n[Error del agente]: {str(e)}\n")
                continue

    finally:
        await db_conn.close()
        # Limpiar base de datos temporal de la sesión
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass


async def main():
    # Validar credenciales de LLM
    if (
        not settings.OPENAI_API_KEY
        and not settings.GEMINI_API_KEY
        and not settings.ANTHROPIC_API_KEY
    ):
        print("Error: No se detectó ninguna API Key de LLM en el archivo .env")
        print("Configura GEMINI_API_KEY (u OPENAI_API_KEY o ANTHROPIC_API_KEY).")
        sys.exit(1)

    await iniciar_agente()


if __name__ == "__main__":
    asyncio.run(main())