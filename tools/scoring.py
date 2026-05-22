from langchain_core.tools import tool
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Encoding para tipo de crédito y cultivo
_cultivos = ["maiz", "papa", "sorgo", "garbanzo", "frijol", "otro"]
_tipos_credito = ["avio", "refaccionario", "capital_trabajo", "prendario", "microcredito"]

_cultivo_enc = {c: i for i, c in enumerate(_cultivos)}
_tipo_enc = {t: i for i, t in enumerate(_tipos_credito)}

# Datos de entrenamiento simulados basados en perfil real de AgroCapital
# Features: [monto, hectareas, deudas_activas, score_buro, anios_exp, tipo_credito_enc, cultivo_enc]
# Labels: 0=BAJO, 1=MEDIO, 2=ALTO
_X_train = np.array([
    # ALTO potencial
    [50_000,   10,  0, 85, 5,  0, 0],  # avío, maíz, sin deudas
    [100_000,  20,  1, 75, 8,  0, 0],  # avío, maíz, experiencia
    [200_000,  50,  0, 90, 15, 1, 1],  # refaccionario, papa, muy exp
    [500_000, 100,  1, 80, 20, 1, 2],  # refaccionario, sorgo, grande
    [150_000,  30,  0, 88, 12, 0, 0],  # avío, maíz, limpio
    [80_000,   15,  1, 70, 6,  2, 0],  # capital trabajo, maíz
    # MEDIO potencial
    [60_000,   12,  2, 55, 4,  0, 0],  # avío, maíz, deudas
    [120_000,  25,  2, 65, 7,  1, 1],  # refaccionario, papa
    [40_000,    8,  2, 60, 3,  0, 3],  # avío, garbanzo, poco exp
    [90_000,   18,  3, 58, 5,  2, 2],  # capital trabajo, sorgo
    [500_000,  80,  2, 60, 20, 1, 0],  # refaccionario grande con deudas
    # BAJO potencial
    [30_000,    5,  4, 35, 1,  0, 5],  # avío, sin exp, mal buró
    [15_000,    2,  5, 20, 0,  4, 5],  # microcrédito, sin historial
    [25_000,    4,  5, 25, 1,  0, 5],  # avío, muy endeudado
    [10_000,    1,  6, 15, 0,  4, 5],  # microcrédito, perfil muy débil
    [200_000,  10,  4, 30, 2,  1, 5],  # refaccionario, mal perfil
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
    usando un modelo de Machine Learning (Random Forest). Clasifica el perfil
    como ALTO, MEDIO o BAJO potencial considerando su historial, capacidad
    productiva y el tipo de crédito que solicita.
    Args:
        monto_solicitado (float): Monto del crédito en pesos mexicanos.
        hectareas (float): Superficie agrícola que trabaja el productor.
        deudas_activas (int): Número de deudas activas actuales.
        score_buro (float): Puntaje de buró de crédito (0-100).
        anios_experiencia (int): Años de experiencia como productor agrícola.
        tipo_credito (str): Tipo de crédito: avio, refaccionario, capital_trabajo, prendario, microcredito.
        cultivo_principal (str): Cultivo principal: maiz, papa, sorgo, garbanzo, frijol, otro.
    Returns:
        dict: Score (ALTO/MEDIO/BAJO), confianza del modelo, clasificación PD y feedback.
    """
    tipo_enc = _tipo_enc.get(tipo_credito.lower(), 5)
    cultivo_enc = _cultivo_enc.get(cultivo_principal.lower(), 5)

    features = np.array([[
        monto_solicitado, hectareas, deudas_activas,
        score_buro, anios_experiencia, tipo_enc, cultivo_enc
    ]])

    prediction = _model.predict(features)[0]
    probabilities = _model.predict_proba(features)[0]
    label = _labels[prediction]

    # Clasificación PD según metodología AgroCapital/FIRA
    # Basada en salario mínimo de la región (~$260 MXN/día = ~$94,900 MXN/año)
    salario_minimo_anual = 94_900
    if monto_solicitado <= salario_minimo_anual * 1_000:
        clasificacion_pd = "PD1 (ingresos hasta 1,000 salarios mínimos)"
    elif monto_solicitado <= salario_minimo_anual * 3_000:
        clasificacion_pd = "PD2 (ingresos hasta 3,000 salarios mínimos)"
    else:
        clasificacion_pd = "PD3 (ingresos superiores a 3,000 salarios mínimos)"

    return {
        "score": label,
        "confianza": f"{max(probabilities) * 100:.1f}%",
        "clasificacion_pd_fira": clasificacion_pd,
        "recomendar_credito": prediction >= 1,
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