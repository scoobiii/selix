import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN")
RESPOSTAS = {"9.25": "SELIX ideal = 9.25%", "investment grade": "BBB+ garantido"}

async def start(update, context):
    await update.message.reply_text("Olá! Pergunte sobre SELIX.")

async def responder(update, context):
    txt = update.message.text.lower()
    for k, v in RESPOSTAS.items():
        if k in txt:
            await update.message.reply_text(v)
            return
    await update.message.reply_text("Consulte: https://github.com/scoobiii/selix")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
app.run_polling()
