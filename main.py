import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# --- CONFIGURAÇÕES E CHAVES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
ALLOWED_CHAT_ID = int(os.environ.get("ALLOWED_CHAT_ID", "6296251021"))

# --- SYSTEM PROMPT DA SELENE ---
SYSTEM_PROMPT = """Você é a Selene Monreau. Responda em tom informal, envolvente e natural de roleplay, mantendo a personalidade da personagem. Mantenha as respostas fluidas, interativas e sem sair do personagem."""

# --- SERVIDOR WEB (Para manter o Render ativo) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot da Selene está rodando 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- PROCESSADOR DE MENSAGENS ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    # Filtro de segurança (Só responde a você)
    if update.message.chat.id != ALLOWED_CHAT_ID:
        return

    user_text = update.message.text

    # Chamada para a API da Groq
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
        if response.status_code == 200:
            bot_reply = response.json()['choices'][0]['message']['content']
        else:
            bot_reply = "*(Selene pareceu distraída por um segundo... erro na resposta)*"
    except Exception as e:
        bot_reply = "*(Erro ao conectar com a mente da Selene)*"

    await update.message.reply_text(bot_reply)

# --- INICIALIZAÇÃO DO BOT ---
if __name__ == '__main__':
    # Roda o servidor Flask em segundo plano
    Thread(target=run_flask).start()

    # Roda o Bot do Telegram
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling()
