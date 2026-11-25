import pandas as pd

df = pd.read_csv("databases/titanic3.csv")


def tot():
    return df.to_json(orient="records")


def supervivencia():
    supervivencia = df.groupby(["pclass", "sex"])["survived"].mean() * 100
    return supervivencia.round(2).to_json(orient="records")


def new_york():
    columnas_interes = ["survived", "name", "sex", "age", "home.dest"]

    usuarios_de_new_york = df[
        df["home.dest"].str.contains("NY", na=False)
    ][columnas_interes]

    return usuarios_de_new_york.to_json(orient="records")


def obtener_datos():
    return df.copy()
