import os
import base64

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def imagem_para_base64(caminho_arquivo):
    with open(caminho_arquivo, "rb") as imagem:
        return base64.b64encode(imagem.read()).decode("utf-8")


def executar_ocr(caminho_arquivo):
    
    imagem_base64 = imagem_para_base64(caminho_arquivo)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um sistema OCR especializado em notas fiscais "
                    "e recibos brasileiros."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extraia TODO o texto presente nesta imagem. "
                            "Retorne apenas o texto bruto."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{imagem_base64}"
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    texto_extraido = response.choices[0].message.content

    return texto_extraido