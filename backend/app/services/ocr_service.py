import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def imagem_para_base64(caminho_arquivo: str) -> str:
    with open(caminho_arquivo, "rb") as imagem:
        return base64.b64encode(imagem.read()).decode("utf-8")


def executar_ocr(caminho_arquivo: str) -> str:
    imagem_base64 = imagem_para_base64(caminho_arquivo)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Extraia todo o texto visível desta nota fiscal, "
                            "recibo ou comprovante. Retorne apenas o texto bruto."
                        )
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{imagem_base64}"
                    }
                ]
            }
        ]
    )

    return response.output_text