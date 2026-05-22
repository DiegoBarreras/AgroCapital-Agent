from langchain_core.tools import tool
from typing import List

# Estratos FIRA por monto en UDIS (1 UDI ≈ 8.5 MXN aprox)
ESTRATOS_FIRA = {
    "microempresa": {"limite_udis": 10_000, "limite_pesos_aprox": 85_000},
    "empresa_familiar": {"limite_udis": 33_000, "limite_pesos_aprox": 280_500},
    "pequena_empresa": {"limite_udis": 160_000, "limite_pesos_aprox": 1_360_000},
    "mediana_empresa": {"limite_udis": 4_000_000, "limite_pesos_aprox": 34_000_000},
    "empresa_grande": {"limite_udis": None, "limite_pesos_aprox": None},
}

PLAZOS_CREDITO = {
    "avio": {"plazo_max_años": 2, "descripcion": "Capital de trabajo, insumos, jornales y gastos directos de producción"},
    "refaccionario": {"plazo_max_años": 15, "descripcion": "Inversiones fijas: maquinaria, equipos, sistemas de riego"},
    "capital_trabajo": {"plazo_max_años": 5, "descripcion": "Capital de trabajo permanente"},
    "prendario": {"plazo_max_dias": 180, "descripcion": "Comercialización con garantía de inventarios"},
    "arrendamiento": {"plazo_max_años": 15, "descripcion": "Adquisición de activos fijos muebles e inmuebles"},
    "microcredito": {"plazo_max_años": 3, "monto_max_udis": 33_000, "descripcion": "Poblaciones hasta 50,000 habitantes"},
}

REQUISITOS_DOCUMENTALES = [
    "INE o identificación oficial vigente",
    "CURP",
    "RFC con homoclave",
    "Comprobante de domicilio (no mayor a 3 meses)",
    "Documentos de tierra (título de propiedad o contrato de arrendamiento vigente)",
    "Plan de inversión o proyecto productivo del ciclo agrícola",
    "Estado de cuenta bancario (últimos 3 meses)",
    "Seguro agrícola de cobertura amplia endosado a favor de AgroCapital",
]

ACTIVIDADES_ELEGIBLES = [
    "producción agrícola",
    "producción ganadera",
    "producción forestal",
    "producción pesquera",
    "agroindustria",
    "comercialización al mayoreo de productos agropecuarios",
    "proveeduría de insumos agrícolas",
    "maquinaria agrícola",
    "sistemas de riego",
]


@tool
def verificar_requisitos_fira(
    documentos_presentados: List[str],
    monto_solicitado_pesos: float,
    tipo_credito: str,
    actividad: str
) -> dict:
    """
    Verifica si un productor agrícola cumple con los requisitos del FIRA
    para ser elegible a crédito fondeado por AgroCapital del Noroeste.
    Valida documentación, estrato empresarial, tipo de crédito y actividad elegible.
    Args:
        documentos_presentados: Lista de nombres de documentos que el productor presenta.
        monto_solicitado_pesos: Monto del crédito solicitado en pesos mexicanos.
        tipo_credito: Tipo de crédito: avio, refaccionario, capital_trabajo, prendario, arrendamiento, microcredito.
        actividad: Actividad productiva del solicitante (ej: producción agrícola, maíz).
    Returns:
        dict: Resultado completo con elegibilidad, estrato, documentos faltantes y feedback.
    """
    documentos_lower = [d.lower() for d in documentos_presentados]
    faltantes = []
    for req in REQUISITOS_DOCUMENTALES:
        palabra_clave = req.split()[0].lower()
        if not any(palabra_clave in doc for doc in documentos_lower):
            faltantes.append(req)

    if monto_solicitado_pesos <= 85_000:
        estrato = "microempresa"
    elif monto_solicitado_pesos <= 280_500:
        estrato = "empresa_familiar"
    elif monto_solicitado_pesos <= 1_360_000:
        estrato = "pequena_empresa"
    elif monto_solicitado_pesos <= 34_000_000:
        estrato = "mediana_empresa"
    else:
        estrato = "empresa_grande"

    tipo_valido = tipo_credito.lower() in PLAZOS_CREDITO
    info_credito = PLAZOS_CREDITO.get(tipo_credito.lower(), {})
    actividad_lower = actividad.lower()
    actividad_elegible = any(act in actividad_lower for act in ACTIVIDADES_ELEGIBLES)

    total_docs = len(REQUISITOS_DOCUMENTALES)
    cumplidos = total_docs - len(faltantes)
    porcentaje = (cumplidos / total_docs) * 100
    elegible = len(faltantes) == 0 and tipo_valido and actividad_elegible

    feedback_partes = []
    if faltantes:
        feedback_partes.append(f"Faltan {len(faltantes)} documento(s): {', '.join(faltantes[:3])}{'...' if len(faltantes) > 3 else ''}.")
    if not tipo_valido:
        feedback_partes.append(f"Tipo de crédito '{tipo_credito}' no reconocido. Opciones: {', '.join(PLAZOS_CREDITO.keys())}.")
    if not actividad_elegible:
        feedback_partes.append(f"La actividad '{actividad}' no está dentro de las elegibles por FIRA.")
    if elegible:
        feedback_partes.append("El productor cumple todos los requisitos FIRA. Puede proceder.")

    return {
        "elegible": elegible,
        "cumplimiento_documental": f"{porcentaje:.0f}%",
        "estrato_fira": estrato,
        "tipo_credito_valido": tipo_valido,
        "actividad_elegible": actividad_elegible,
        "documentos_faltantes": faltantes,
        "info_credito_solicitado": info_credito,
        "feedback": " ".join(feedback_partes),
    }


@tool
def consultar_productos_agrocapital(tipo_credito: str = "") -> dict:
    """
    Consulta información sobre los productos de crédito de AgroCapital del Noroeste,
    fondeados por FIRA. Útil para orientar al productor sobre qué producto necesita.
    Args:
        tipo_credito: Tipo específico a consultar (avio, refaccionario, capital_trabajo, prendario, microcredito). Si está vacío devuelve todos.
    Returns:
        dict: Información de productos con plazos, montos y requisitos.
    """
    productos = {
        "avio": {
            "nombre": "Crédito de Habilitación o Avío",
            "objetivo": "Capital de trabajo: semillas, fertilizantes, jornales",
            "plazo_maximo": "2 años por ciclo productivo",
            "monto_minimo": "$10,000 MXN",
            "requisito_especial": "Seguro agrícola endosado a AgroCapital + garantías FEGA",
            "cultivos_principales": ["maíz", "papa", "sorgo", "garbanzo", "frijol"],
        },
        "refaccionario": {
            "nombre": "Crédito Refaccionario",
            "objetivo": "Inversión fija: maquinaria, tractores, sistemas de riego",
            "plazo_maximo": "15 años",
            "monto_minimo": "$50,000 MXN",
            "requisito_especial": "Seguro agrícola + garantías según capacidad de pago",
        },
        "capital_trabajo": {
            "nombre": "Crédito de Capital de Trabajo",
            "objetivo": "Línea revolvente para liquidez operativa",
            "plazo_maximo": "180 días por disposición, hasta 3 años de vigencia",
            "monto_minimo": "$10,000 MXN",
            "requisito_especial": "Garantías suficientes",
        },
        "prendario": {
            "nombre": "Crédito Prendario",
            "objetivo": "Comercialización usando inventarios como garantía",
            "plazo_maximo": "180 días prorrogable otros 180",
            "monto_minimo": "$500,000 MXN",
            "requisito_especial": "Seguro de mercancías + certificados de depósito",
        },
        "microcredito": {
            "nombre": "Microcrédito",
            "objetivo": "Liquidez para pequeños productores",
            "plazo_maximo": "3 a 15 meses",
            "monto_maximo": "$100,000 MXN",
            "requisito_especial": "Actividad productiva documentada",
        },
    }

    if tipo_credito and tipo_credito.lower() in productos:
        return {"producto": productos[tipo_credito.lower()]}

    return {"productos_disponibles": productos}