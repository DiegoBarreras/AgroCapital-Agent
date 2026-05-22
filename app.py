"""
AgroAssistant - Interfaz Web para Productores Agrícolas
AgroCapital del Noroeste, S.A. de C.V.

Ejecución:
    uv run streamlit run app.py
"""

import asyncio
import uuid
import threading

import streamlit as st

from config.config import settings
from core.engine import create_deep_agent, run_agent
from prompts.agrocapital import AGROCAPITAL_AGENT_PROMPT
from tools import ALL_TOOLS

st.set_page_config(
    page_title="AgroAssistant | AgroCapital",
    page_icon="🌾",
    layout="centered",
)

st.markdown("""
<style>
    .stApp { background-color: #f5f7f0; }
    .main-header {
        background: linear-gradient(135deg, #1a5c2a, #2d8a45);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.8rem; }
    .main-header p { color: #c8f0d0; margin: 0.3rem 0 0 0; font-size: 0.95rem; }
    .chat-message-user {
        background: #2d8a45;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 12px 12px 2px 12px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    .chat-message-bot {
        background: white;
        color: #1a1a1a;
        padding: 0.75rem 1rem;
        border-radius: 12px 12px 12px 2px;
        margin: 0.5rem 0;
        max-width: 85%;
        border-left: 4px solid #2d8a45;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .status-badge {
        background: #e8f5e9;
        color: #2d8a45;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🌾 AgroAssistant</h1>
    <p>Agente Inteligente de Crédito Agrícola · AgroCapital del Noroeste</p>
</div>
""", unsafe_allow_html=True)

# ── Event loop dedicado en hilo separado ─────────────────────────────────────
def _run_in_thread(coro):
    """Corre una corutina en un hilo con su propio event loop."""
    result = [None]
    error = [None]

    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result[0] = loop.run_until_complete(coro)
        except Exception as e:
            error[0] = e
        finally:
            loop.close()

    t = threading.Thread(target=run)
    t.start()
    t.join()

    if error[0]:
        raise error[0]
    return result[0]


# ── Inicialización de sesión ─────────────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False


async def get_response(mensaje: str, thread_id: str) -> str:
    agent, conn = await create_deep_agent(
        system_prompt=AGROCAPITAL_AGENT_PROMPT,
        tools=ALL_TOOLS,
        provider=settings.LLM_PROVIDER,
        model_name=settings.LLM_MODEL,
        db_path=f"./session_{thread_id[:8]}.db",
    )
    try:
        return await run_agent(
            agent=agent,
            task=mensaje,
            thread_id=thread_id,
        )
    finally:
        await conn.close()


# ── Historial ────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="chat-message-bot">
        👋 Bienvenido a <strong>AgroAssistant</strong>, el asistente de crédito agrícola de AgroCapital del Noroeste.<br><br>
        Estoy aquí para ayudarle a evaluar su solicitud de crédito y orientarle en el proceso con FIRA.<br><br>
        ¿En qué le puedo ayudar hoy?
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-message-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message-bot">{msg["content"]}</div>', unsafe_allow_html=True)

# ── Input ────────────────────────────────────────────────────────────────────
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        entrada = st.text_input(
            "Mensaje",
            placeholder="Ej: Quiero un crédito avío para mi cosecha de maíz en Culiacán",
            label_visibility="collapsed",
        )
    with col2:
        enviar = st.form_submit_button("Enviar 📤", use_container_width=True)

# ── Procesar ─────────────────────────────────────────────────────────────────
if enviar and entrada.strip() and not st.session_state.processing:
    st.session_state.processing = True
    st.session_state.messages.append({"role": "user", "content": entrada})

    with st.spinner("AgroAssistant está procesando..."):
        try:
            respuesta = _run_in_thread(
                get_response(entrada, st.session_state.thread_id)
            )
        except Exception as e:
            respuesta = f"Lo siento, ocurrió un error: {str(e)}"
        finally:
            st.session_state.processing = False

    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    st.rerun()

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div style="text-align:center"><span class="status-badge">🟢 Agente Activo</span></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div style="text-align:center;color:#888;font-size:0.8rem">Sesión: {st.session_state.thread_id[:8]}...</div>', unsafe_allow_html=True)
with col3:
    if st.button("🔄 Nueva sesión"):
        st.session_state.clear()
        st.rerun()