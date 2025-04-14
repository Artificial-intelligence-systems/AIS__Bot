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
- Порог уверенности ответа (минимум 98.8%)

Основные улучшения:
- Улучшенная система распознавания ключевых слов с использованием регулярных выражений
- Оптимизированная структура обработки запросов:
  • Разделение ключевых слов на категории
  • Динамическое формирование контекста для каждой категории
- Повышенный порог уверенности ответа (с 95% до 98.8%)
- Добавлена логировка запросов и ответов
- Добавлена новая категория товаров "телевизоры"

Изменения в обработке запросов:
- Реализована система приоритетов ответов (выбор наиболее точного)
- Улучшена обработка словоформ (разные окончания слов)
- Оптимизирована структура данных для быстрого доступа

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
import re
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
        "/start - запуск бота\n"
        "/help - помощь с взаимодействием"
        ""
        "Вы можете производить поиск необходимого обородования для этого достаточно запрос вида есть ли в наличии телефоны\n"
        "Также можно производить поиск по истории компании для этого достаточно просто написать вопрос\n"
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
    global answer_text
    try:
        keyword_patterns = {
            'ноутбук': re.compile(r'ноутбук[а-я]*', re.IGNORECASE),
            'телефон': re.compile(r'телефон[а-я]*', re.IGNORECASE),
            'игр консол': re.compile(r'игр[а-я]*\s*консол[а-я]*', re.IGNORECASE),
            'наушник': re.compile(r'наушник[а-я]*', re.IGNORECASE),
            'телевиз': re.compile(r'телевиз[а-я]*', re.IGNORECASE),
            'скидк': re.compile(r'скидк[а-я]*', re.IGNORECASE),
            'цен': re.compile(r'цен[а-я]*', re.IGNORECASE),
            'характерист': re.compile(r'характерист[а-я]*', re.IGNORECASE)
        }

        keyword_context_map = {
            'ноутбук': f"ноутбуки:  {', '.join(products_db['ноутбуки'])}",
            'телефон': f"телефоны:  {', '.join(products_db['телефоны'])}",
            'игр консол': f"игровые консоли:  {', '.join(products_db['игровые консоли'])}",
            'наушник': f"наушники:  {', '.join(products_db['наушники'])}",
            'телевиз': f"телевизоры:  {', '.join(products_db['телевизоры'])}",
            'скидк': "",
            'цен': "",
            'характерист': ""
        }

        text = message.text.lower()

        matched_keywords = [
            keyword for keyword, pattern in keyword_patterns.items()
            if pattern.search(text)
        ]

        if matched_keywords:
            accuracy_answer = 0
            for keyword in matched_keywords:
                context = keyword_context_map[keyword]
                answer = model([context], [message.text])

                if (answer and isinstance(answer, list) and answer[0] and answer[0][0] and answer[2][0] >= 0.988
                        and answer[2][0] >= 0.988 and answer[2][0] > accuracy_answer):
                    answer_text = answer[0]
                    accuracy_answer = answer[2][0]
                    print(text + ", " +  answer[0][0],  answer[2][0])
                    print(context)
                else:
                    answer_text = "Информация не найдена о товарах."
                    print(text, answer[0][0], answer[2][0])
        else:
            answer = model([dns_history], [message.text])

            if answer and isinstance(answer, list) and answer[0] and answer[0][0] and answer[2][0] >= 0.988:
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