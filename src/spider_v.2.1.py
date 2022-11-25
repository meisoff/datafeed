"""
Этат парсер получает данные с карточки товара в формате:
            "price": int,
            "isAvailable": bool
Удалил все сохранения в Датафрейм и в файл
Парсер просто возвращает объект формата выше.
Подключите базу в данное возвращение (строки 194 - 203)
"""

import pandas as pd
import datetime
import logging
import undetected_chromedriver as uc
import time
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re
import requests
import crud

class SpiderRadugaFile:
    def __init__(self):
        self.data = None
        self.driver = uc.Chrome()
        self.api = "https://www.ozon.ru/api/composer-api.bx/page/json/v2?url="
        logging.basicConfig(level=logging.INFO, force=True, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.region_dict = [
    {
        "number": 1,
        "region": "Екатеринбург",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=2763c110-cb8b-416a-9dac-ad28a55b4402&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },
    {
        "number": 2,
        "region": "Санкт-Петербург",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=c2deb16a-0330-4f05-821f-1d09c93331e6&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },
    {
        "number": 3,
        "region": "Москва",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=0c5b2444-70a0-4932-980c-b4dc0d3f02b5&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },
    {
        "number": 4,
        "region": "Нижний Новгород",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=555e7d61-d9a7-4ba6-9770-6caa8198c483&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },
    {
        "number": 5,
        "region": "Пермь",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=a309e4ce-2f36-4106-b1ca-53e0f48a6d95&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },
    {
        "number": 6,
        "region": "Новосибирск",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=8dea00e3-9aab-4d8e-887c-ef2aaa546456&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },
    {
        "number": 0,
        "region": "Казань",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=93b3df57-4c89-44df-ac42-96f05e9cd3b9&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },
    {
        "number": 7,
        "region": "Челябинск",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=a376e68d-724a-4472-be7c-891bdb09ae32&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },
    {
        "number": 8,
        "region": "Краснодар",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=7dfa745e-aa19-4688-b121-b655c11e482f&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },
    {
        "number": 9,
        "region": "Самара",
        "link": "/modal/city_selector?neaf=f&pv=0&searchCity=&select_location=bb035cc3-1dc2-4627-9d25-a1bf2d4b936b&src_main=%2F&src_modal=%2Fmodal%2Faddressbook%3Fsrc_main%3D%252F"
    },

]
        self.url_chg_region = "https://www.ozon.ru"
        self.result_dict = []

    def start_parse(self):
        message_start = "*** Начало работы: {} ***".format(datetime.datetime.now().strftime('%d.%m в %H:%M'))
        message_end = "*** Работа парсера завершена. Формируем файл ***"

        self.alarm_message(message_start)
        logging.info(message_start)

        self.data = self.get_data()  # Получаем инфу для парсера
        self.parse(self.data)  # Запускаем парсер

        # !!!! ОТПРАВЛЯЕМ МАССИВ С СЛОВАРЯМИ В БАЗУ ДАННЫХ !!!!
        # crud.create_many_result(self.result_dict)

        self.alarm_message(message_end)
        logging.info(message_end)

    def alarm_message(self, message: str) -> None:
        base_url = 'https://alarmerbot.ru/'
        requests.post(base_url, {'key': "b03eff-400216-1b28f4", 'message': message})

    def get_data(self):
        data = pd.DataFrame(crud.get_items_for_parsing())  # Получаем словарь, создаем фрейм
        data = data.sort_values(by=['region'])  # Сортируем фрейм, чтобы постоянно не менять регион парсера
        return data

    def select_region(self, number: int):
        for item in self.region_dict:
            if item["number"] == number:
                self.url_chg_region += item["link"]
                logging.info("*** Выбрали регион: {} ***".format(item["region"]))
        # Меняем регион
        self.driver.get(self.url_chg_region)

    def parse(self, data):

        use_region = None

        for s, item in data.iterrows():
            index = item['index']
            link = item['link']
            region = item['region']
            formula = item['formula']

            if use_region != region:
                use_region = region
                self.select_region(use_region)

            url = f'{self.api + link}'  # .replace("https://www.ozon.ru", "")
            logging.info("Получаем данные с - {}".format(link))

            # Идем по ссылке
            try:
                # Ставим ожидание загрузки страницы не более 10 секунд
                self.driver.set_page_load_timeout(10)

                self.driver.get(url)
                response = self.driver.find_element(By.TAG_NAME, "pre").text
                time.sleep(0.5)

            except (NoSuchElementException, TimeoutException) as e:
                logging.warning(f'Ошибка! {e.msg}')
                self.driver.quit()
                time.sleep(10)
                self.driver = uc.Chrome()
                # Ставим ожидание загрузки страницы не более 10 секунд
                self.driver.set_page_load_timeout(10)
                # Меняем регион
                self.driver.get(self.url_chg_region)
                # Идем по ссылке
                self.driver.get(url)
                response = self.driver.find_element(By.TAG_NAME, "pre").text

            try:
                data = json.loads(response)
                widgets = data.get('widgetStates')

                price = None
                is_available = False

                for key, value in widgets.items():
                    if 'webSale' in key:
                        if json.loads(value).get('offers'):
                            prices = json.loads(value).get('offers')[0]
                        else:
                            prices = json.loads(value).get('offer')

                        if prices.get('price'):
                            price = re.search(r'[0-9]+', prices.get('price').replace(u'\u2009', ''))[0]
                        else:
                            price = 0
                        if prices.get('isAvailable'):
                            is_available = True

                crud.create_result(
                    {
                        "index": index,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S"),
                        "url": link,
                        "region": region,
                        "price": round(eval(price + formula), 2) if formula else price,
                        "stock": is_available
                    }
                )

            except AttributeError as e:
                logging.warning("Ошибка! {}".format(e))

            except TypeError:
                logging.warning("Итерация по NoneType")

            finally:
                logging.info("Получение данных по ссылке завершено.")

if __name__ == "__main__":
    SpiderRadugaFile().start_parse()