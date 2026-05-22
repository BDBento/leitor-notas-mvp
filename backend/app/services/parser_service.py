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

    padroes_prioritarios = [
        r"R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})",
        r"R\$\s*([0-9]+[.,][0-9]{2})",
        r"Pix enviado\s*R\$\s*([0-9]+[.,][0-9]{2})",
    ]

    for padrao in padroes_prioritarios:
        match = re.search(padrao, texto, re.IGNORECASE)

        if match:
            return normalizar_valor(match.group(1))

    candidatos = re.findall(
        r"(?<![\d])([0-9]{1,5}[.,][0-9]{2})(?![\d])",
        texto
    )

    valores_validos = []

    for candidato in candidatos:
        valor = normalizar_valor(candidato)

        if valor is None:
            continue

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
            return datetime.strptime(
                match.group(1),
                "%d/%m/%Y"
            ).date()
        except ValueError:
            pass

    # Formato com traço: 12-05-2026
    match = re.search(r"(\d{2}-\d{2}-\d{4})", texto)

    if match:
        try:
            return datetime.strptime(
                match.group(1),
                "%d-%m-%Y"
            ).date()
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

    linhas = [
        linha.strip()
        for linha in texto.split("\n")
        if linha.strip()
    ]

    ignorar = [
        "nome",
        "cpf/cnpj",
        "cpf",
        "cnpj",
        "instituição",
        "instituicao",
        "agência",
        "agencia",
        "conta",
        "tipo de conta",
        "origem",
        "destino",
        "valor",
        "tipo de transferência",
        "tipo de transferencia",
        "id da transação",
        "id da transacao",
        "comprovante de",
        "transferência",
        "transferencia",
        "pix",
    ]

    def linha_valida(linha):
        linha_lower = linha.lower()

        # Ignora linhas técnicas
        if "tipo" in linha_lower:
            return False

        if "transferencia" in linha_lower:
            return False

        if "transacao" in linha_lower:
            return False

        if "id da transacao" in linha_lower:
            return False

        if "tipo de transferencia" in linha_lower:
            return False

        if "tipo de transferencia pix" in linha_lower:
            return False

        if "idcda" in linha_lower:
            return False

        if "valor" in linha_lower:
            return False

        if "r$" in linha_lower:
            return False

        if "comprovante" in linha_lower:
            return False

        # Ignora valores monetários
        if re.search(r"\b\d+[,.]\d{2}\b", linha_lower):
            return False

        # Ignora datas textuais
        if re.search(
            r"\d{1,2}\s+(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)\s+\d{4}",
            linha_lower
        ):
            return False

        # Ignora datas comuns
        if re.search(r"\d{2}/\d{2}/\d{4}", linha_lower):
            return False

        # Ignora horários
        if re.search(r"\d{2}:\d{2}", linha_lower):
            return False

        # Ignora linhas compostas apenas por números
        if re.search(r"^\d+$", linha_lower):
            return False

        # Ignora CPF/CNPJ
        if re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", linha):
            return False

        # Ignora mascaras
        if re.search(r"\*{2,}", linha):
            return False

        # Ignora termos da lista
        if any(item == linha_lower for item in ignorar):
            return False

        # Ignora rodapé/app
        if any(item in linha_lower for item in [
            "pagamentos s.a",
            "ouvidoria",
            "estamos aqui",
            "me ajuda",
            "http",
            "www.",
            "atendimento",
        ]):
            return False

        # Linha muito pequena
        if len(linha.strip()) < 4:
            return False

        return True

    # NUBANK / PIX
    # Destino -> Nome -> Pessoa
    for i, linha in enumerate(linhas):

        if "destino" in linha.lower():

            bloco = linhas[i + 1:i + 12]

            for j, item in enumerate(bloco):

                if "nome" in item.lower():

                    # Nome na mesma linha
                    partes = item.split("Nome")

                    if len(partes) > 1:
                        candidato = partes[1].strip()

                        if (
                            len(candidato.split()) >= 2
                            and linha_valida(candidato)
                        ):
                            return candidato

                    # Nome na próxima linha
                    if j + 1 < len(bloco):
                        candidato = bloco[j + 1]

                        candidato = (
                            candidato
                            .replace("Nome", "")
                            .strip()
                        )

                        if (
                            len(candidato.split()) >= 2
                            and linha_valida(candidato)
                        ):
                            return candidato

    # Quem recebeu
    for i, linha in enumerate(linhas):

        if "quem recebeu" in linha.lower():

            bloco = linhas[i + 1:i + 12]

            for j, item in enumerate(bloco):

                if "nome" in item.lower():

                    # Nome na mesma linha
                    partes = item.split("Nome")

                    if len(partes) > 1:
                        candidato = partes[1].strip()

                        if (
                            len(candidato.split()) >= 2
                            and linha_valida(candidato)
                        ):
                            return candidato

                    # Nome na próxima linha
                    if j + 1 < len(bloco):
                        candidato = bloco[j + 1]

                        candidato = (
                            candidato
                            .replace("Nome", "")
                            .strip()
                        )

                        if (
                            len(candidato.split()) >= 2
                            and linha_valida(candidato)
                        ):
                            return candidato

    # Caso genérico
    for i, linha in enumerate(linhas):

        if "nome" == linha.lower():

            if i + 1 < len(linhas):

                candidato = linhas[i + 1]

                if (
                    len(candidato.split()) >= 2
                    and linha_valida(candidato)
                ):
                    return candidato

    # Fallback genérico
    for linha in linhas:

        if (
            len(linha.split()) >= 2
            and linha_valida(linha)
        ):
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