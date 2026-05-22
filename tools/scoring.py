from langchain_core.tools import tool
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Costo máximo por hectárea según cultivo (crédito avío, Sinaloa)
COSTO_MAX_POR_HECTAREA = {
    "maiz": 12500,
    "papa": 40000,
    "sorgo": 7000,
    "garbanzo": 8000,
    "frijol": 6000,
    "otro": 10000,
}

_cultivos = ["maiz", "papa", "sorgo", "garbanzo", "frijol", "otro"]
_tipos_credito = ["avio", "refaccionario", "capital_trabajo", "prendario", "microcredito"]

_cultivo_enc = {c: i for i, c in enumerate(_cultivos)}
_tipo_enc = {t: i for i, t in enumerate(_tipos_credito)}

_X_train = np.array([
    [50_000,   10,  0, 85, 5,  0, 0],
    [100_000,  20,  1, 75, 8,  0, 0],
    [200_000,  50,  0, 90, 15, 1, 1],
    [500_000, 100,  1, 80, 20, 1, 2],
    [150_000,  30,  0, 88, 12, 0, 0],
    [80_000,   15,  1, 70, 6,  2, 0],
    [60_000,   12,  2, 55, 4,  0, 0],
    [120_000,  25,  2, 65, 7,  1, 1],
    [40_000,    8,  2, 60, 3,  0, 3],
    [90_000,   18,  3, 58, 5,  2, 2],
    [500_000,  80,  2, 60, 20, 1, 0],
    [30_000,    5,  4, 35, 1,  0, 5],
    [15_000,    2,  5, 20, 0,  4, 5],
    [25_000,    4,  5, 25, 1,  0, 5],
    [10_000,    1,  6, 15, 0,  4, 5],
    [200_000,  10,  4, 30, 2,  1, 5],
])

_y_train = np.array([2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0])

_model = RandomForestClassifier(n_estimators=50, random_state=42)
_model.fit(_X_train, _y_train)

_labels = {0: "BAJO", 1: "MEDIO", 2: "ALTO"}

_feedback = {
    2: "Perfil sólido. Proceder con solicitud de documentación FIRA completa y análisis formal de crédito.",
    1: "Perfil viable con condiciones. Se recomienda revisar nivel de endeudamiento o reforzar garantías antes de proceder.",
    0: "Perfil no cumple criterios mínimos en este momento. Se recomienda mejorar historial crediticio, reducir deudas activas o acumular más experiencia productiva antes de volver a solicitar.",
}


@tool
def score_lead(
    monto_solicitado: float,
    hectareas: float,
    deudas_activas: int,
    score_buro: float,
    anios_experiencia: int,
    tipo_credito: str,
    cultivo_principal: str,
) -> dict:
    """
    Evalúa la viabilidad crediticia de un productor agrícola para AgroCapital
    usando Machine Learning (Random Forest). Clasifica el perfil como ALTO, MEDIO
    o BAJO considerando historial, capacidad productiva, tipo de crédito y cultivo.
    También valida que el monto solicitado sea razonable según las hectáreas y cultivo.
    Args:
        monto_solicitado: Monto del crédito en pesos mexicanos.
        hectareas: Superficie agrícola que trabaja el productor.
        deudas_activas: Número de deudas activas actuales.
        score_buro: Puntaje de buró de crédito (0-100).
        anios_experiencia: Años de experiencia como productor agrícola.
        tipo_credito: Tipo de crédito: avio, refaccionario, capital_trabajo, prendario, microcredito.
        cultivo_principal: Cultivo principal: maiz, papa, sorgo, garbanzo, frijol, otro.
    Returns:
        dict: Score (ALTO/MEDIO/BAJO), confianza, clasificación PD, validación por hectárea y feedback.
    """
    tipo_enc = _tipo_enc.get(tipo_credito.lower(), 4)
    cultivo_enc = _cultivo_enc.get(cultivo_principal.lower(), 5)

    features = np.array([[
        monto_solicitado, hectareas, deudas_activas,
        score_buro, anios_experiencia, tipo_enc, cultivo_enc
    ]])

    prediction = _model.predict(features)[0]
    probabilities = _model.predict_proba(features)[0]
    label = _labels[prediction]

    # Validación de monto por hectárea según cultivo
    costo_max = COSTO_MAX_POR_HECTAREA.get(cultivo_principal.lower(), 10000)
    monto_maximo_recomendado = hectareas * costo_max
    monto_excedido = monto_solicitado > monto_maximo_recomendado

    alerta_monto = None
    if monto_excedido:
        alerta_monto = (
            f"El monto solicitado (${monto_solicitado:,.0f}) supera el techo recomendado "
            f"para {hectareas} ha de {cultivo_principal} "
            f"(${monto_maximo_recomendado:,.0f} máx). "
            f"Se recomienda justificar el excedente con plan de inversión detallado."
        )
        # Bajar score si el monto excede por más del 30%
        if monto_solicitado > monto_maximo_recomendado * 1.3 and prediction > 0:
            prediction = max(0, prediction - 1)
            label = _labels[prediction]

    # Clasificación PD según metodología AgroCapital/FIRA
    salario_minimo_anual = 94_900
    if monto_solicitado <= salario_minimo_anual * 1_000:
        clasificacion_pd = "PD1 (ingresos hasta 1,000 salarios mínimos)"
    elif monto_solicitado <= salario_minimo_anual * 3_000:
        clasificacion_pd = "PD2 (ingresos hasta 3,000 salarios mínimos)"
    else:
        clasificacion_pd = "PD3 (ingresos superiores a 3,000 salarios mínimos)"

    resultado = {
        "score": label,
        "confianza": f"{max(probabilities) * 100:.1f}%",
        "clasificacion_pd_fira": clasificacion_pd,
        "recomendar_credito": prediction >= 1,
        "monto_maximo_recomendado": f"${monto_maximo_recomendado:,.0f} MXN",
        "monto_excedido": monto_excedido,
        "feedback": _feedback[prediction],
        "factores_evaluados": {
            "monto": monto_solicitado,
            "hectareas": hectareas,
            "deudas_activas": deudas_activas,
            "score_buro": score_buro,
            "anios_experiencia": anios_experiencia,
            "tipo_credito": tipo_credito,
            "cultivo": cultivo_principal,
        }
    }

    if alerta_monto:
        resultado["alerta_monto"] = alerta_monto

    return resultado