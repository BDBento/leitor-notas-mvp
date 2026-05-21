import re
from datetime import datetime


def limpar_texto(texto: str) -> str:
    return texto.replace("\r", "\n").strip()


def normalizar_valor(valor: str):
    if not valor:
        return None

    valor = valor.strip()
    valor = valor.replace("R$", "")
    valor = valor.replace(" ", "")

    # Caso brasileiro: 1.234,56
    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    else:
        # Caso OCR retorne 86.75
        valor = valor

    try:
        return float(valor)
    except ValueError:
        return None


def extrair_valor(texto: str):
    texto = limpar_texto(texto)

    # 1. Primeiro tenta pegar valor logo após R$
    padroes_prioritarios = [
        r"R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})",
        r"R\$\s*([0-9]+[.,][0-9]{2})",
        r"Pix enviado\s*R\$\s*([0-9]+[.,][0-9]{2})",
    ]

    for padrao in padroes_prioritarios:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return normalizar_valor(match.group(1))

    # 2. Fallback: pega valores monetários, ignorando CPF/CNPJ e identificadores
    candidatos = re.findall(r"(?<![\d])([0-9]{1,5}[.,][0-9]{2})(?![\d])", texto)

    valores_validos = []

    for candidato in candidatos:
        valor = normalizar_valor(candidato)

        if valor is None:
            continue

        # evita valores absurdos causados por CPF/documentos
        if 0 < valor < 100000:
            valores_validos.append(valor)

    if valores_validos:
        return valores_validos[0]

    return None


def extrair_data(texto: str):
    texto = limpar_texto(texto)

    # Formato comum: 12/05/2026
    match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)

    if match:
        try:
            return datetime.strptime(match.group(1), "%d/%m/%Y").date()
        except ValueError:
            pass

    # Formato com traço: 12-05-2026
    match = re.search(r"(\d{2}-\d{2}-\d{4})", texto)

    if match:
        try:
            return datetime.strptime(match.group(1), "%d-%m-%Y").date()
        except ValueError:
            pass

    # Formato Nubank: 18 MAI 2026
    meses = {
        "JAN": "01",
        "FEV": "02",
        "MAR": "03",
        "ABR": "04",
        "MAI": "05",
        "JUN": "06",
        "JUL": "07",
        "AGO": "08",
        "SET": "09",
        "OUT": "10",
        "NOV": "11",
        "DEZ": "12",
    }

    match = re.search(
        r"(\d{1,2})\s+(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+(\d{4})",
        texto,
        re.IGNORECASE
    )

    if match:
        dia = match.group(1).zfill(2)
        mes = meses.get(match.group(2).upper())
        ano = match.group(3)

        if mes:
            try:
                return datetime.strptime(
                    f"{dia}/{mes}/{ano}",
                    "%d/%m/%Y"
                ).date()
            except ValueError:
                pass

    return None


def extrair_estabelecimento(texto: str):
    texto = limpar_texto(texto)
    linhas = [linha.strip() for linha in texto.split("\n") if linha.strip()]

    # Caso Pix: tenta pegar o nome depois de "Quem recebeu"
    for i, linha in enumerate(linhas):
        if "quem recebeu" in linha.lower():
            for proxima in linhas[i + 1:i + 8]:
                texto_linha = proxima.strip()

                if texto_linha.lower() in ["nome", "cpf/cnpj", "instituição", "instituicao"]:
                    continue

                if len(texto_linha) > 3 and not re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto_linha):
                    return texto_linha

    # Caso encontre padrão "Nome" antes do recebedor
    for i, linha in enumerate(linhas):
        if linha.lower() == "nome" and i + 1 < len(linhas):
            candidato = linhas[i + 1]

            if len(candidato) > 3:
                return candidato

    # Fallback genérico: primeira linha útil
    ignorar = [
        "pix enviado",
        "sobre a transação",
        "sobre a transacao",
        "data do pagamento",
        "horário",
        "horario",
        "identificador",
        "id da transação",
        "id da transacao",
        "quem recebeu",
        "quem pagou",
        "nome",
        "cpf/cnpj",
        "instituição",
        "instituicao",
    ]

    for linha in linhas:
        linha_limpa = linha.lower()

        if any(item in linha_limpa for item in ignorar):
            continue

        if len(linha) > 5:
            return linha

    return "Não identificado"


def classificar_categoria(texto: str):
    texto = texto.lower()

    categorias = {
        "Mercado": [
            "comper",
            "assaí",
            "atacadão",
            "supermercado",
            "extra",
            "mercado",
            "fort",
        ],

        "Transporte": [
            "uber",
            "99",
            "posto",
            "gasolina",
            "combustivel",
            "shell",
            "ipiranga",
        ],

        "Farmácia": [
            "drogasil",
            "droga raia",
            "farmacia",
            "ultrafarma",
        ],

        "Alimentação": [
            "ifood",
            "restaurante",
            "pizza",
            "burger",
            "hamburguer",
            "lanchonete",
        ],

        "Pix": [
            "pix",
            "comprovante pix",
            "transferencia pix",
        ],

        "Saúde": [
            "hospital",
            "clinica",
            "laboratorio",
            "consulta",
        ],
    }

    for categoria, palavras in categorias.items():
        for palavra in palavras:
            if palavra in texto:
                return categoria

    return "Outros"

