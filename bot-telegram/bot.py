import os
import tempfile
import requests

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")
BOT_USER_EMAIL = os.getenv("BOT_USER_EMAIL")
BOT_USER_PASSWORD = os.getenv("BOT_USER_PASSWORD")


def obter_token_backend():
    if not BOT_USER_EMAIL or not BOT_USER_PASSWORD:
        raise RuntimeError("BOT_USER_EMAIL ou BOT_USER_PASSWORD não configurados no .env")

    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": BOT_USER_EMAIL,
            "senha": BOT_USER_PASSWORD
        },
        timeout=30
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Erro ao autenticar no backend. "
            f"Status: {response.status_code}. "
            f"Resposta: {response.text}"
        )

    return response.json()["access_token"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Envie uma foto de nota fiscal, recibo ou comprovante para eu processar."
    )


async def receber_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Imagem recebida. Processando...")

    try:
        foto = update.message.photo[-1]
        arquivo = await context.bot.get_file(foto.file_id)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
            caminho_temp = temp.name

        await arquivo.download_to_drive(caminho_temp)

        token = obter_token_backend()

        with open(caminho_temp, "rb") as imagem:
            files = {
                "file": ("nota.jpg", imagem, "image/jpeg")
            }

            headers = {
                "Authorization": f"Bearer {token}"
            }

            response = requests.post(
                f"{BACKEND_URL}/upload/",
                files=files,
                headers=headers,
                timeout=120
            )

        os.remove(caminho_temp)

        if response.status_code != 200:
            await update.message.reply_text(
                "Não consegui processar essa imagem. Verifique o backend."
            )
            return

        dados = response.json()

        mensagem = (
            "Nota processada com sucesso!\n\n"
            f"ID: {dados.get('gasto_id')}\n"
            f"Estabelecimento: {dados.get('estabelecimento') or 'Não identificado'}\n"
            f"Data: {dados.get('data_gasto') or 'Não identificada'}\n"
            f"Valor: {dados.get('valor_total') or 'Não identificado'}\n"
            f"Status: {dados.get('status')}"
        )

        await update.message.reply_text(mensagem)

    except Exception as erro:
        await update.message.reply_text(
            f"Erro ao processar a imagem: {str(erro)}"
        )


async def receber_documento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Por enquanto envie como foto. Depois vamos aceitar PDF e documentos."
    )


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN não configurado no .env")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, receber_foto))
    app.add_handler(MessageHandler(filters.Document.ALL, receber_documento))

    print("Bot Telegram iniciado e aguardando imagens...", flush=True)

    app.run_polling()


if __name__ == "__main__":
    main()