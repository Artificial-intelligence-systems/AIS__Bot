"""
ТЕЛЕГРАМ-БОТ ДЛЯ МАГАЗИНА DNS

Назначение:
- Предоставление информации о товарах магазина DNS
- Ответы на вопросы об истории компании

Основные функции:
- Обработка естественного языка с помощью модели DeepPavlov (ruBERT-QA)
- Автоматическое определение типа запроса:
  • О товарах -> поиск в базе продуктов
  • О компании -> поиск в истории DNS

Команды:
- /start - приветственное сообщение
- /help - примеры запросов
"""

import telebot
import os
from answeringModel import get_answer_squad_ru_bert

token = os.getenv('TOKEN')
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот-помощник магазина DNS. Задавайте вопросы о товарах или истории компании.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "/start - запуск бота\n"
        "/help - помощь с взаимодействием"
        ""
        "Вы можете производить поиск необходимого обородования для этого достаточно запрос вида есть ли в наличии телефоны\n"
        "Также можно производить поиск по истории компании для этого достаточно просто написать вопрос\n"
        ""
        "Примеры вопросов:\n"
        "- Какие ноутбуки есть в наличии?\n"
        "- Ноутбук [Название без скобочек] цена\n"
        "- Ноутбук [Название без скобочек] характеристики\n"
        "- Когда основали DNS?\n"
        "- Какие собственные бренды у DNS?"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.lower()
    answer_text = get_answer_squad_ru_bert(text)
    bot.send_message(message.chat.id, answer_text)


if __name__ == '__main__':
    print("Бот запущен...")
    bot.delete_webhook()
    bot.polling(none_stop=True)