from langchain_core.tools import tool

REQUISITOS_FIRA = [
    "INE o identificación oficial vigente",
    "CURP",
    "RFC con homoclave",
    "Comprobante de domicilio (no mayor a 3 meses)",
    "Documentos de tierra (título de propiedad o contrato de arrendamiento vigente)",
    "Plan de inversión o proyecto productivo del ciclo agrícola",
    "Estado de cuenta bancario (últimos 3 meses)",
]

@tool
def verificar_requisitos_fira(documentos_presentados: list) -> dict:
    """
    Verifica si un productor agrícola cumple con los requisitos documentales del FIRA
    para ser elegible a crédito fondeado por AgroCapital.
    Args:
        documentos_presentados (list): Lista de documentos que el productor dice tener.
    Returns:
        dict: Documentos faltantes, cumplimiento porcentual y si es elegible para continuar.
    """
    documentos_lower = [d.lower() for d in documentos_presentados]
    faltantes = []

    for req in REQUISITOS_FIRA:
        palabra_clave = req.split()[0].lower()
        if not any(palabra_clave in doc for doc in documentos_lower):
            faltantes.append(req)

    total = len(REQUISITOS_FIRA)
    cumplidos = total - len(faltantes)
    porcentaje = (cumplidos / total) * 100
    elegible = len(faltantes) == 0

    return {
        "elegible": elegible,
        "cumplimiento": f"{porcentaje:.0f}%",
        "documentos_faltantes": faltantes if faltantes else [],
        "mensaje": (
            "El productor cumple con toda la documentación requerida por FIRA. Puede proceder."
            if elegible else
            f"Faltan {len(faltantes)} documento(s) requeridos por FIRA. No se puede proceder hasta completarlos."
        )
    }