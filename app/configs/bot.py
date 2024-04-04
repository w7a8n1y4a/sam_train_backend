import telebot

from app import settings


tbot = telebot.TeleBot(token=settings.telegram_token, skip_pending=True, threaded=False)
