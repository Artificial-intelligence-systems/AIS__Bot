"""
DNS Assistant - система обработки пользовательских запросов для интернет-магазина

Основной функционал:
1. Анализ входящих сообщений и классификация запросов по категориям:
   - Товары (ноутбуки, телефоны, игровые консоли и др.)
   - Атрибуты товаров (скидки, цены, характеристики)
   - Информация о компании

2. Многоуровневая система обработки запросов:
   - Поиск ключевых слов с использованием регулярных выражений
   - Комбинированная обработка сложных запросов (товар + атрибут)
   - Приоритетный порядок проверки категорий запросов

3. Использование модели squad_ru_bert:
   - Поиск ответов в подготовленных контекстах
   - Оценка точности ответов (accuracy >= 0.988)
   - Выбор наиболее релевантного ответа

4. Подготовленные базы данных:
   - Каталог товаров (products_db)
   - Каталог товаров с характеристиками (products_db_char)
   - Информация о компании (dns_history)

5. Основные компоненты класса DNSAssistant:
    1) __init__(self) - Инициализация объекта ассистента
    2) _initialize_keyword_patterns(self) - Настройка системы распознавания ключевых слов
    3) _initialize_context_maps(self) - Подготовка контекстов для генерации ответов
    4) _find_matching_keywords(self, message_text, category) - Поиск ключевых слов в запросе
    5) _get_best_answer(self, message_text, contexts) Выбор оптимального ответа
    6) _handle_product_query(self, message_text, product_keywords, attribute_keywords) - Обработка запросов о товарах
    7) _handle_attribute_query(self, message_text, attribute_keywords) - Обработка запросов об атрибутах
    8) _handle_company_query(self, message_text) - Обработка запросов о компании
    9) reply_request(self, message_text) - Основной публичный интерфейс класса

Пример использования:
    assistant = DNSAssistant()
    response = assistant.reply_request("Какие ноутбуки есть в наличии?")
"""

from dotenv import load_dotenv
import re
from deeppavlov import build_model
from contexts.productStorage import products_db, products_db_char
from contexts.historyCompany import dns_history

load_dotenv()

class AnsweringModel_squad_ru_bert:
    def __init__(self):
        #self.model = build_model('squad_ru_bert', download=True, install=True)
        self.model = build_model('squad_ru_bert', download=False, install=False)
        self._initialize_keyword_patterns()
        self._initialize_context_maps()

    def _initialize_keyword_patterns(self):
        self.keyword_patterns = {
            'products': {
                'ноутбук': re.compile(r'ноутбук[а-я]*', re.IGNORECASE),
                'телефон': re.compile(r'телефон[а-я]*', re.IGNORECASE),
                'игр консол': re.compile(r'игр[а-я]*\s*консол[а-я]*', re.IGNORECASE),
                'наушник': re.compile(r'наушник[а-я]*', re.IGNORECASE),
                'телевиз': re.compile(r'телевиз[а-я]*', re.IGNORECASE),
            },
            'attributes': {
                'скидк': re.compile(r'скидк[а-я]*', re.IGNORECASE),
                'цен': re.compile(r'цен[а-я]*', re.IGNORECASE),
                'характерист': re.compile(r'характерист[а-я]*', re.IGNORECASE)
            }
        }

    def _initialize_context_maps(self):
        self.context_maps = {
            'products': {
                'ноутбук': f"ноутбуки: {', '.join(products_db['ноутбуки'])}",
                'телефон': f"телефоны: {', '.join(products_db['телефоны'])}",
                'игр консол': f"игровые консоли: {', '.join(products_db['игровые консоли'])}",
                'наушник': f"наушники: {', '.join(products_db['наушники'])}",
                'телевиз': f"телевизоры: {', '.join(products_db['телевизоры'])}",
            },
            'attributes': {
                'цен':{
                    'ноутбук': f"ноутбуки: {', '.join(products_db_char['ноутбуки'])}",
                    'телефон': f"телефоны: {', '.join(products_db_char['телефоны'])}",
                    'игр консол': f"игровые консоли: {', '.join(products_db['игровые консоли'])}",
                    'наушник': f"наушники: {', '.join(products_db_char['наушники'])}",
                    'телевиз': f"телевизоры: {', '.join(products_db_char['телевизоры'])}",
                },
                'характерист': {
                    'ноутбук': f"ноутбуки: {', '.join(products_db_char['ноутбуки'])}",
                    'телефон': f"телефоны: {', '.join(products_db_char['телефоны'])}",
                    'игр консол': f"игровые консоли: {', '.join(products_db['игровые консоли'])}",
                    'наушник': f"наушники: {', '.join(products_db_char['наушники'])}",
                    'телевиз': f"телевизоры: {', '.join(products_db_char['телевизоры'])}",
                }
            },
            'company': dns_history
        }

    def _find_matching_keywords(self, message_text, category):
        return [
            keyword for keyword, pattern in self.keyword_patterns[category].items()
            if pattern.search(message_text)
        ]

    def _get_best_answer(self, message_text, contexts):
        best_answer = None
        max_accuracy = 0

        for context in contexts:
            answer = self.model([context], [message_text])

            if (answer and isinstance(answer, list) and answer[0] and answer[0][0]
                    and answer[2][0] >= 0.988 and answer[2][0] > max_accuracy):
                max_accuracy = answer[2][0]
                best_answer = answer[0][0]
                print(f"{message_text}, {answer[0][0]}, {answer[2][0]}")
                print(f"{context}")

        return best_answer, max_accuracy

    def _handle_product_query(self, message_text, product_keywords, attribute_keywords):
        contexts = []

        if product_keywords and attribute_keywords:
            for product in product_keywords:
                for attribute in attribute_keywords:
                    context = (self.context_maps['attributes'][attribute][product])
                    contexts.append(context)

        if product_keywords and not contexts:
            contexts = [self.context_maps['products'][p] for p in product_keywords]

        best_answer, accuracy = self._get_best_answer(message_text, contexts)

        if not best_answer and product_keywords:
            product_contexts = [self.context_maps['products'][p] for p in product_keywords]
            best_answer, accuracy = self._get_best_answer(message_text, product_contexts)

        return best_answer

    def _handle_attribute_query(self, message_text, attribute_keywords):
        contexts = [self.context_maps['attributes'][a] for a in attribute_keywords]
        best_answer, _ = self._get_best_answer(message_text, contexts)
        return best_answer

    def _handle_company_query(self, message_text):
        answer = self.model([self.context_maps['company']], [message_text])

        if (answer and isinstance(answer, list) and answer[0] and answer[0][0] and answer[2][0] >= 0.988):
            return answer[0][0]
        return None

    def reply_request(self, message_text):
        try:
            product_keywords = self._find_matching_keywords(message_text, 'products')
            attribute_keywords = self._find_matching_keywords(message_text, 'attributes')

            if product_keywords:
                answer = self._handle_product_query(message_text, product_keywords, attribute_keywords)
                if answer:
                    return answer

            if attribute_keywords:
                answer = self._handle_attribute_query(message_text, attribute_keywords)
                if answer:
                    return answer

            answer = self._handle_company_query(message_text)
            if answer:
                return answer

            return "Информация не найдена. Попробуйте уточнить ваш запрос."

        except Exception as e:
            print(f"Ошибка: {e}")
            return "Произошла ошибка. Попробуйте сформулировать иначе."


assistant = AnsweringModel_squad_ru_bert()
get_answer_squad_ru_bert = assistant.reply_request