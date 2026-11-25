import requests
import pandas as pd
import matplotlib.pyplot as plt

URL = "http://127.0.0.1:8000"

print("Cliente conectado a la API del Titanic")

pasajeros = []
skip = 0
limit = 100

while True:
    respuesta = requests.get(
        f"{URL}/elements",
        params={"skip": skip, "limit": limit}
    )

    datos = respuesta.json()

    pasajeros.extend(datos["resultados"])

    print(f"Descargados: {len(pasajeros)} pasajeros")

    if skip + limit >= datos["total"]:
        break

    skip += limit

print("Descarga completada")

df = pd.DataFrame(pasajeros)

print("\nPrimeros pasajeros:")
print(df.head())

print("\nInformación del DataFrame:")
print(df.info())

print("\nDimensiones del DataFrame:")
print(df.shape)

# Limpiar valores nulos
df["age"] = df["age"].fillna(df["age"].median())
df["fare"] = df["fare"].fillna(df["fare"].median())
df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])

# Comprobar valores nulos restantes
print("\nValores nulos después de la limpieza:")
print(df.isnull().sum())

# Analizar supervivencia por clase y sexo
analisis = df.groupby(["pclass", "sex"])["survived"].mean() * 100

print("\nPorcentaje de supervivencia por clase y sexo:")
print(analisis.round(2))

# Crear dashboard
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Gráfico 1: Supervivientes y fallecidos
df["survived"].value_counts().sort_index().plot(
    kind="bar",
    ax=axes[0]
)

axes[0].set_title("Supervivientes y fallecidos")
axes[0].set_xlabel("0 = Fallecidos / 1 = Supervivientes")
axes[0].set_ylabel("Número de pasajeros")

# Gráfico 2: Supervivencia por clase
(df.groupby("pclass")["survived"].mean() * 100).plot(
    kind="bar",
    ax=axes[1]
)

axes[1].set_title("Supervivencia según la clase")
axes[1].set_xlabel("Clase del pasajero")
axes[1].set_ylabel("Supervivencia (%)")

plt.tight_layout()

# Guardar dashboard
plt.savefig("dashboard_titanic.png")

plt.show()

print("\nDashboard guardado correctamente.")

# Crear un pasajero de prueba
nuevo_pasajero = {
    "pclass": 1,
    "survived": 1,
    "name": "Pasajero creado desde client.py",
    "sex": "male",
    "age": 30,
    "sibsp": 0,
    "parch": 0,
    "fare": 50,
    "embarked": "S"
}

# Obtener el siguiente ID disponible
total = requests.get(f"{URL}/").json()["total_registros"]
id_prueba = total + 1

respuesta = requests.post(
    f"{URL}/elements",
    json=nuevo_pasajero
)

print("\nResultado del POST:", respuesta.status_code)
print(respuesta.json())

# Eliminar el pasajero de prueba
respuesta = requests.delete(
    f"{URL}/elements/{id_prueba}"
)

print("\nResultado del DELETE:", respuesta.status_code)
print(respuesta.json())