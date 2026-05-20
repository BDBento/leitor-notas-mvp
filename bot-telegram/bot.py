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


def obter_token_backend(update):
    user = update.effective_user

    response = requests.post(
        f"{BACKEND_URL}/auth/telegram-login",
        json={
            "telegram_user_id": str(user.id),
            "nome": user.full_name,
            "username": user.username
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
    user = update.effective_user

    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/telegram-login",
            json={
                "telegram_user_id": str(user.id),
                "nome": user.full_name,
                "username": user.username
            },
            timeout=30
        )

        if response.status_code != 200:
            await update.message.reply_text(
                f"Erro ao criar acesso.\n"
                f"Status: {response.status_code}\n"
                f"Resposta: {response.text[:500]}"
            )
            return

        dados = response.json()
        usuario = dados["usuario"]
        senha_temporaria = dados.get("senha_temporaria")

        mensagem = (
            f"Olá, {user.first_name}!\n\n"
            "Seu acesso foi configurado com sucesso.\n\n"
            f"Login Web:\n{usuario['email']}\n"
        )

        if senha_temporaria:
            mensagem += f"Senha temporária:\n{senha_temporaria}\n\n"
        else:
            mensagem += "\nVocê já possui cadastro ativo.\n\n"

        mensagem += (
            "Acesse o painel em:\n"
            "http://localhost:5173\n\n"
            "Agora envie uma foto de nota fiscal, recibo ou comprovante Pix."
        )

        await update.message.reply_text(mensagem)

    except Exception as erro:
        await update.message.reply_text(
            f"Erro ao criar acesso:\n{str(erro)}"
        )

async def receber_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Imagem recebida. Processando...")

    try:
        foto = update.message.photo[-1]
        arquivo = await context.bot.get_file(foto.file_id)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
            caminho_temp = temp.name

        await arquivo.download_to_drive(caminho_temp)

        token = obter_token_backend(update)

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
    
    
async def resetar_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/telegram-reset-password",
            json={
                "telegram_user_id": str(user.id),
                "nome": user.full_name,
                "username": user.username
            },
            timeout=30
        )

        if response.status_code != 200:
            await update.message.reply_text(
                f"Não consegui resetar sua senha.\n"
                f"Status: {response.status_code}\n"
                f"Resposta: {response.text[:500]}"
            )
            return

        dados = response.json()

        await update.message.reply_text(
            "Sua senha temporária foi redefinida.\n\n"
            f"Login Web:\n{dados['email']}\n\n"
            f"Nova senha:\n{dados['senha_temporaria']}\n\n"
            "Acesse:\nhttp://localhost:5173"
        )

    except Exception as erro:
        await update.message.reply_text(
            f"Erro ao resetar senha:\n{str(erro)}"
        )
    


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN não configurado no .env")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("senha", resetar_senha))
    app.add_handler(MessageHandler(filters.PHOTO, receber_foto))
    app.add_handler(MessageHandler(filters.Document.ALL, receber_documento))

    print("Bot Telegram iniciado e aguardando imagens...", flush=True)

    app.run_polling()


if __name__ == "__main__":
    main()
    
