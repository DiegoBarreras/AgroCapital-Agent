from langchain_core.tools import tool
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Modelo entrenado con datos simulados de productores agrícolas
_X_train = np.array([
    [50000, 10, 0, 85, 5],
    [100000, 20, 1, 75, 8],
    [200000, 50, 0, 90, 15],
    [30000, 5, 3, 40, 1],
    [500000, 100, 2, 60, 20],
    [15000, 2, 5, 20, 0],
    [80000, 15, 1, 70, 6],
    [25000, 4, 4, 30, 1],
    [150000, 30, 0, 88, 12],
    [60000, 12, 2, 55, 4],
])
_y_train = np.array([2, 2, 2, 0, 1, 0, 2, 0, 2, 1])  # 0=BAJO, 1=MEDIO, 2=ALTO

_model = RandomForestClassifier(n_estimators=10, random_state=42)
_model.fit(_X_train, _y_train)

_labels = {0: "BAJO", 1: "MEDIO", 2: "ALTO"}
_feedback = {
    0: "El perfil no cumple los criterios mínimos de AgroCapital. Score de buró bajo, alto nivel de endeudamiento o experiencia insuficiente.",
    1: "El perfil es viable con condiciones. Se recomienda revisar nivel de deuda o aumentar garantías.",
    2: "El perfil es sólido. Proceder con solicitud de documentación FIRA completa.",
}

@tool
def score_lead(
    monto_solicitado: float,
    hectareas: float,
    deudas_activas: int,
    score_buro: float,
    anios_experiencia: int
) -> dict:
    """
    Evalúa la viabilidad crediticia de un productor agrícola para AgroCapital.
    Usa un modelo de Machine Learning para clasificar el perfil como ALTO, MEDIO o BAJO potencial.
    Args:
        monto_solicitado (float): Monto del crédito solicitado en pesos.
        hectareas (float): Superficie agrícola que trabaja el productor.
        deudas_activas (int): Número de deudas activas actuales.
        score_buro (float): Puntaje de buró de crédito del productor (0-100).
        anios_experiencia (int): Años de experiencia como productor agrícola.
    Returns:
        dict: Resultado con score (ALTO/MEDIO/BAJO), probabilidad y retroalimentación.
    """
    features = np.array([[monto_solicitado, hectareas, deudas_activas, score_buro, anios_experiencia]])
    prediction = _model.predict(features)[0]
    probabilities = _model.predict_proba(features)[0]
    label = _labels[prediction]

    return {
        "score": label,
        "confianza": f"{max(probabilities) * 100:.1f}%",
        "feedback": _feedback[prediction],
        "recomendar_credito": prediction >= 1
    }