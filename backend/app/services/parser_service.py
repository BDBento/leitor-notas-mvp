import re
from datetime import datetime


def extrair_valor(texto: str):
    valores = re.findall(r"(\d+[.,]\d{2})", texto)

    if not valores:
        return None

    valor = valores[-1].replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except ValueError:
        return None


def extrair_data(texto: str):
    datas = re.findall(r"(\d{2}/\d{2}/\d{4})", texto)

    if not datas:
        return None

    try:
        return datetime.strptime(datas[0], "%d/%m/%Y").date()
    except ValueError:
        return None


def extrair_estabelecimento(texto: str):
    linhas = texto.split("\n")

    for linha in linhas:
        linha = linha.strip()

        if len(linha) > 5:
            return linha

    return "Não identificado"