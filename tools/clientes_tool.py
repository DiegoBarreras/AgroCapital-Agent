from langchain_core.tools import tool
from typing import Optional
import csv
import os

# Ruta al CSV de clientes
_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "clientes.csv")

def _cargar_clientes() -> list:
    """Carga el CSV de clientes en memoria."""
    clientes = []
    try:
        with open(_CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                clientes.append(row)
    except FileNotFoundError:
        pass
    return clientes


@tool
def consultar_cliente(identificador: str) -> dict:
    """
    Consulta el expediente de un cliente existente de AgroCapital por su ID o nombre.
    Útil para verificar si un productor ya tiene historial con AgroCapital antes de
    iniciar una nueva solicitud de crédito.
    Args:
        identificador: ID del cliente (ej: AC001) o nombre completo o parcial.
    Returns:
        dict: Expediente del cliente o mensaje de que no existe registro.
    """
    clientes = _cargar_clientes()
    identificador_lower = identificador.lower()

    for cliente in clientes:
        if (cliente['id'].lower() == identificador_lower or
                identificador_lower in cliente['nombre'].lower()):
            return {
                "encontrado": True,
                "expediente": {
                    "id": cliente['id'],
                    "nombre": cliente['nombre'],
                    "telefono": cliente['telefono'],
                    "ubicacion": f"{cliente['municipio']}, {cliente['estado']}",
                    "cultivo_principal": cliente['cultivo_principal'],
                    "hectareas": float(cliente['hectareas']),
                    "score_buro": float(cliente['score_buro']),
                    "deudas_activas": int(cliente['deudas_activas']),
                    "anios_experiencia": int(cliente['anios_experiencia']),
                    "tipo_credito": cliente['tipo_credito'],
                    "monto_solicitado": float(cliente['monto_solicitado']),
                    "estatus": cliente['estatus'],
                }
            }

    return {
        "encontrado": False,
        "mensaje": f"No se encontró ningún cliente con el identificador '{identificador}' en el sistema de AgroCapital. El productor no tiene historial previo."
    }


@tool
def listar_clientes_por_estatus(estatus: str) -> dict:
    """
    Lista todos los clientes de AgroCapital filtrados por estatus para seguimiento comercial.
    Args:
        estatus: Estado del cliente: activo, revision, rechazado.
    Returns:
        dict: Lista de clientes con ese estatus y resumen.
    """
    clientes = _cargar_clientes()
    filtrados = [c for c in clientes if c['estatus'].lower() == estatus.lower()]

    return {
        "estatus": estatus,
        "total": len(filtrados),
        "clientes": [
            {
                "id": c['id'],
                "nombre": c['nombre'],
                "municipio": c['municipio'],
                "cultivo": c['cultivo_principal'],
                "monto": float(c['monto_solicitado']),
            }
            for c in filtrados
        ]
    }