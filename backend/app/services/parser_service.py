import re
from datetime import datetime


def extrair_valor(texto):
    padrao = r"(\d+[.,]\d{2})"

    valores = re.findall(padrao, texto)

    if not valores:
        return None

    valor = valores[-1]

    valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except:
        return None


def extrair_data(texto):
    padrao = r"(\d{2}/\d{2}/\d{4})"

    datas = re.findall(padrao, texto)

    if not datas:
        return None

    try:
        return datetime.strptime(datas[0], "%d/%m/%Y").date()
    except:
        return None


def extrair_estabelecimento(texto):
    linhas = texto.split("\n")

    for linha in linhas:
        linha = linha.strip()

        if len(linha) > 5:
            return linha

    return "Não identificado"