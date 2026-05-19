import pytesseract
from PIL import Image


def executar_ocr(caminho_arquivo: str) -> str:
    imagem = Image.open(caminho_arquivo)

    texto = pytesseract.image_to_string(
        imagem,
        lang="por"
    )

    return texto.strip()