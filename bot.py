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
- Порог уверенности ответа (минимум 95%)

Источники данных:
- products_db (productStorage.py) - база данных товаров
- dns_history (historyCompany.py) - история компании

Команды:
- /start - приветственное сообщение
- /help - примеры запросов

Зависимости: telebot, python-dotenv, deeppavlov
"""

import telebot
import os
from dotenv import load_dotenv
from deeppavlov import build_model
from productStorage import products_db
from historyCompany import  dns_history

load_dotenv()
token = os.getenv('TOKEN')

bot = telebot.TeleBot(token)

model = build_model('squad_ru_bert', download=False, install=False)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот-помощник магазина DNS. Задавайте вопросы о товарах или истории компании.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "/start - запуск бота"
        "/help - помощь с взаимодействием"
        ""
        "Вы можете производить поиск необходимого обородования для этого достаточно запрос вида есть ли в наличии телефоны"
        "Также можно производить поиск по истории компании для этого достаточно просто написать вопрос"
        ""
        "Примеры вопросов:\n"
        "- Какие ноутбуки есть в наличии?\n"
        "- Есть ли скидки на телефоны?\n"
        "- Когда основали DNS?\n"
        "- Какие собственные бренды у DNS?"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        # any заменить на более оптимизированную структуру
        # разделить ключевые слова на блоки + реализовать разделение контекста длч этих групп
        # реализовать полноценное логирование по шаблону [вопрос, ответ, точность]
        if any(keyword in message.text.lower() for keyword in ['ноутбук', 'телефон', 'игр консол', 'наушник', 'скидк', 'цен', 'товар', 'характерист']):

            context = "\n".join(
                f"--- {key} ---\n" + "\n".join(items)
                for key, items in products_db.items()
            )
            answer = model([context], [message.text])

            if answer and isinstance(answer, list) and answer[0] and answer[0][0] and answer[2][0] >= 0.95:
                answer_text = answer[0]
                print(answer)
            else:
                answer_text = "Информация не найдена о товарах."
        else:
            answer = model([dns_history], [message.text])

            if answer and isinstance(answer, list) and answer[0] and answer[0][0] and answer[2][0] >= 0.95:
                answer_text = answer[0]
                print(answer)
            else:
                answer_text = "Информация не найдена о компании."

        bot.send_message(message.chat.id, answer_text)

    except Exception as e:
        print(f"Ошибка: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте сформулировать иначе.")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
