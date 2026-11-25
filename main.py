from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from dataset import obtener_datos
import pandas as pd

app = FastAPI(
    title="API Titanic",
    description="API REST para consultar y gestionar datos del Titanic",
    version="1.0"
)

class Pasajero(BaseModel):
    pclass: int = Field(ge=1, le=3)
    survived: int = Field(ge=0, le=1)
    name: str = Field(min_length=2)
    sex: str
    age: float = Field(gt=0, le=100)
    sibsp: int = Field(ge=0)
    parch: int = Field(ge=0)
    fare: float = Field(ge=0)
    embarked: str

# Copia de los datos para trabajar con ellos
df = obtener_datos()

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API del Titanic",
        "total_registros": len(df),
        "documentacion": "/docs"
    }

@app.get("/elements")
async def read_elements(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sex: str = None,
    pclass: int = None,
    survived: int = None,
    search: str = None
):
    resultados = df.copy()

    # Filtrar por sexo
    if sex:
        resultados = resultados[
            resultados["sex"].str.lower() == sex.lower()
        ]

    # Filtrar por clase
    if pclass is not None:
        resultados = resultados[
            resultados["pclass"] == pclass
        ]

    # Filtrar por supervivencia
    if survived is not None:
        resultados = resultados[
            resultados["survived"] == survived
        ]

    # Buscar por nombre
    if search:
        resultados = resultados[
            resultados["name"].str.contains(
                search, case=False, na=False
            )
        ]
  # Calcular el total de resultados
    total = len(resultados)

    # Aplicar paginación
    resultados = resultados.iloc[skip:skip + limit]

    # Sustituir valores NaN por None
    resultados = resultados.astype(object).where(
        pd.notna(resultados), None
    )

    # Devolver los resultados
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "resultados": resultados.to_dict(orient="records")
    }
@app.get("/elements/{id}")
async def read_element(id: int):
    if id < 1 or id > len(df):
        raise HTTPException(
            status_code=404,
            detail="Pasajero no encontrado"
        )

    pasajero = df.iloc[id - 1]

    # Sustituir valores NaN por None
    pasajero = pasajero.astype(object).where(
        pd.notna(pasajero), None
    )
    
    return pasajero.to_dict()

@app.post("/elements", status_code=201)
async def create_element(pasajero: Pasajero):

    global df

    nuevo_pasajero = pasajero.model_dump()

    # Añadir las columnas que faltan
    for columna in df.columns:
        if columna not in nuevo_pasajero:
            nuevo_pasajero[columna] = None

    df = pd.concat(
        [df, pd.DataFrame([nuevo_pasajero])],
        ignore_index=True
    )

    return {
        "message": "Pasajero creado correctamente",
        "pasajero": nuevo_pasajero
    }

@app.delete("/elements/{id}")
async def delete_element(id: int):

    global df

    if id < 1 or id > len(df):
        raise HTTPException(
            status_code=404,
            detail="Pasajero no encontrado"
        )

    # Eliminar el pasajero
    df = df.drop(index=id - 1).reset_index(drop=True)

    return {
        "message": "Pasajero eliminado correctamente",
        "id": id
    }
