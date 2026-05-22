from langchain_core.tools import tool
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate
from hubspot.crm.contacts.exceptions import ApiException
import os

def _get_client():
    api_key = os.getenv("HUBSPOT_API_KEY")
    if not api_key:
        raise ValueError("HUBSPOT_API_KEY no configurada en .env")
    return HubSpot(access_token=api_key)


@tool
def registrar_prospecto_hubspot(
    nombre: str,
    telefono: str,
    email: str = "",
    municipio: str = "",
    cultivo: str = "",
    hectareas: float = 0,
    monto_solicitado: float = 0,
    score_resultado: str = "",
    estatus: str = "nuevo_prospecto",
) -> dict:
    """
    Registra o actualiza un prospecto agrícola en el CRM de HubSpot de AgroCapital.
    Se debe llamar automáticamente después de evaluar a un productor con score_lead.
    Args:
        nombre: Nombre completo del productor.
        telefono: Número de teléfono en formato internacional.
        email: Correo electrónico (opcional).
        municipio: Municipio donde produce.
        cultivo: Cultivo principal del productor.
        hectareas: Superficie agrícola en hectáreas.
        monto_solicitado: Monto del crédito solicitado en pesos.
        score_resultado: Resultado del scoring: ALTO, MEDIO o BAJO.
        estatus: Estado del prospecto (nuevo_prospecto, en_revision, aprobado, rechazado).
    Returns:
        dict: Confirmación del registro con ID del contacto en HubSpot.
    """
    try:
        client = _get_client()

        # Separar nombre y apellido
        partes = nombre.strip().split(" ", 1)
        firstname = partes[0]
        lastname = partes[1] if len(partes) > 1 else ""

        propiedades = {
            "firstname": firstname,
            "lastname": lastname,
            "phone": telefono,
            "city": municipio,
            "hs_lead_status": estatus.upper(),
        }

        if email:
            propiedades["email"] = email

        # Notas adicionales en el campo de descripción
        notas = []
        if cultivo:
            notas.append(f"Cultivo: {cultivo}")
        if hectareas:
            notas.append(f"Hectareas: {hectareas}")
        if monto_solicitado:
            notas.append(f"Monto solicitado: ${monto_solicitado:,.0f} MXN")
        if score_resultado:
            notas.append(f"Score AgroCapital: {score_resultado}")

        if notas:
            propiedades["description"] = " | ".join(notas)

        input_data = SimplePublicObjectInputForCreate(properties=propiedades)
        response = client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=input_data
        )

        return {
            "registrado": True,
            "hubspot_id": response.id,
            "nombre": nombre,
            "estatus": estatus,
            "mensaje": f"Prospecto {nombre} registrado exitosamente en HubSpot CRM con ID {response.id}.",
        }

    except ApiException as e:
        # Si el contacto ya existe (409), intentar actualizar
        if e.status == 409:
            return {
                "registrado": False,
                "mensaje": f"El contacto {nombre} ya existe en HubSpot CRM. Expediente previo encontrado.",
            }
        return {
            "registrado": False,
            "mensaje": f"Error al registrar en HubSpot: {str(e)}",
        }
    except Exception as e:
        return {
            "registrado": False,
            "mensaje": f"Error inesperado al conectar con HubSpot: {str(e)}",
        }