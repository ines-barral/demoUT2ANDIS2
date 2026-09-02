from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.reglas.registro import obtener_regla

app = FastAPI(
    title="API Cinta Transportadora - Demo UT2",
    description="Sanity check de paquetes antes de ingresar a la cinta transportadora.",
    version="1.0.0",
)


class Paquete(BaseModel):
    tipo_paquete: str
    peso_kg: float
    alto_cm: float
    ancho_cm: float
    largo_cm: float


@app.get("/")
def health():
    """Endpoint para confirmar que el servicio está arriba."""
    return {"status": "ok"}


@app.post("/paquetes")
def recibir_paquete(paquete: Paquete):
    """
    Sanity check antes de dejar avanzar el paquete por la cinta (RNF-1, Protección).

    Si el tipo de paquete no está registrado, o si no cumple los límites de su tipo,
    se rechaza con 422 y un motivo explícito: la cinta "se frena" en vez de dejar
    avanzar un paquete inseguro y fallar más adelante.
    """
    regla = obtener_regla(paquete.tipo_paquete)
    if regla is None:
        raise HTTPException(
            status_code=422,
            detail=f"tipo_paquete '{paquete.tipo_paquete}' no está registrado",
        )

    es_valido, motivo = regla.es_valido(paquete.model_dump())
    if not es_valido:
        raise HTTPException(status_code=422, detail=motivo)

    return {"estado": "aceptado", "mensaje": "Paquete admitido en la cinta"}