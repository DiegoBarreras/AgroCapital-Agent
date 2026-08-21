# AgroAssistant — Agente Inteligente de Crédito Agrícola

**3er lugar — Build Day: Agentes Inteligentes | Facultad de Ingeniería Mochis, Universidad Autónoma de Sinaloa**

AgroAssistant es un agente de inteligencia artificial conversacional desarrollado para **AgroCapital del Noroeste, S.A. de C.V., SOFOM E.N.R.**, financiera perteneciente a Grupo Ceres y fondeada por el FIRA (Fideicomisos Instituidos en Relación con la Agricultura). El agente acompaña a productores agrícolas en su proceso de solicitud de crédito: evalúa su viabilidad crediticia, verifica requisitos documentales y notifica resultados de forma autónoma.

---

## Problema

El proceso de pre-calificación crediticia en una financiera agrícola es lento y manual. Un productor desconoce si califica, qué documentos necesita y cuánto tiempo tardará en recibir respuesta. Los asesores invierten tiempo considerable en casos que no prosperan. AgroAssistant reduce ese proceso de días a minutos.

---

## Solución

Un agente ReAct construido sobre LangGraph que recibe la solicitud del productor en lenguaje natural, ejecuta un conjunto de herramientas especializadas y devuelve una evaluación completa con retroalimentación accionable — tanto si el productor califica como si no.

---

## Funcionalidades

- **Scoring crediticio con Machine Learning** — Modelo Random Forest entrenado con perfiles del sector agrícola. Evalúa 7 variables del productor y clasifica su perfil como ALTO, MEDIO o BAJO potencial siguiendo la metodología PD1/PD2/PD3 del FIRA. Incluye validación de monto solicitado según superficie y cultivo declarado.
- **Verificación documental FIRA** — Contrasta los documentos presentados contra los requisitos del fideicomiso e identifica faltantes con precisión.
- **Consulta de expedientes** — Búsqueda de clientes existentes por ID o nombre para dar seguimiento a prospectos recurrentes.
- **Integración CRM** — Registro automático de cada prospecto evaluado en HubSpot con nombre, contacto, cultivo, monto y resultado del scoring.
- **Notificaciones WhatsApp** — Confirmaciones y resultados enviados al productor vía Twilio en puntos clave del proceso.
- **Interfaz web** — Chat accesible desde el navegador construido con Streamlit.
- **Webhook** — Endpoint FastAPI para recibir mensajes entrantes de WhatsApp y procesarlos con el agente.
- **Persistencia de sesión** — Historial de conversaciones almacenado localmente con SQLite.

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Agente | LangGraph + LangChain |
| LLM | Claude Haiku 4.5 (Anthropic) |
| Machine Learning | Scikit-learn — Random Forest |
| CRM | HubSpot API |
| Mensajería | Twilio WhatsApp |
| Almacenamiento | AWS S3 + Textract OCR |
| Backend | FastAPI |
| Interfaz | Streamlit |
| Persistencia | SQLite (aiosqlite) |
| Gestión de paquetes | uv |

---

## Instalación

### Requisitos previos
- Python 3.11 o superior
- [uv](https://astral.sh/uv)

### Pasos

```bash
git clone https://github.com/DiegoBarreras/AgroCapital-Agent.git
cd AgroCapital-Agent
uv sync
cp .env.example .env
```

Edita `.env` con tus credenciales antes de ejecutar.

### Variables de entorno

```env
# LLM — configurar al menos una
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=

LLM_PROVIDER=anthropic
LLM_MODEL=claude-haiku-4-5-20251001

# CRM
HUBSPOT_API_KEY=

# WhatsApp
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# AWS (opcional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_S3_BUCKET=
```

---

## Ejecución

**Interfaz web**
```bash
uv run streamlit run app.py
```

**Terminal — modo asesor**
```bash
uv run python main.py
```

**Webhook WhatsApp**
```bash
# Terminal 1
uv run python webhook.py

# Terminal 2
ngrok http 8000
```

---

## Estructura del Proyecto

```
AgroCapital-Agent/
├── app.py                  # Interfaz web Streamlit
├── main.py                 # Chat en terminal (modo asesor)
├── webhook.py              # Webhook FastAPI para WhatsApp
├── config/                 # Configuración centralizada
├── core/                   # Motor LangGraph
├── prompts/
│   └── agrocapital.py      # System prompt especializado
├── tools/
│   ├── scoring.py          # Scoring crediticio con Random Forest
│   ├── fira.py             # Verificación de requisitos FIRA
│   ├── clientes_tool.py    # Consulta de expedientes
│   ├── hubspot_tool.py     # Integración HubSpot CRM
│   ├── cloud/              # AWS S3 y Textract
│   └── whatsapp/           # Twilio WhatsApp
├── data/
│   └── clientes.csv        # Dataset simulado de clientes
└── memory/                 # Memoria semántica
```

---

## Ejemplo de interacción

```
Productor:
  Hola, soy Pedro Inzunza de El Fuerte, Sinaloa. Quiero un crédito avío de
  480,000 pesos para 60 hectáreas de maíz. Llevo 22 años sembrando, sin
  deudas activas y con score de buró de 91.

AgroAssistant:
  Buenas tardes, Pedro. He evaluado su perfil con nuestro sistema de scoring
  crediticio. Su calificación es ALTO potencial (92.3% de confianza),
  clasificación PD1 según metodología FIRA. Puede proceder con la
  documentación formal. He registrado su expediente en el sistema y recibirá
  una confirmación por WhatsApp. ¿Cuenta actualmente con seguro agrícola
  vigente endosado a AgroCapital?
```

---

## Equipo

Desarrollado en el **Build Day: Agentes Inteligentes** organizado por la Facultad de Ingeniería Mochis, Universidad Autónoma de Sinaloa.

Agradecemos a **AgroCapital del Noroeste / Grupo Ceres** por proporcionar el reto y a **Zed Industries** por patrocinar el evento.

---

## Licencia

MIT
