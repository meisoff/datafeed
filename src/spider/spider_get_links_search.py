import datetime
import json
import undetected_chromedriver.v2 as uc
import pandas as pd
from collections import Counter
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
import logging
import os


class SpiderGetLinksSearch:
    def __init__(self):
        self.api = "https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=/search/?from_global=true&layout_container=searchMegapagination&layout_page_index={}&page={}&text={}"
        self.api_brand = "https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=/search/?from_global=true&text={}"
        self.driver = uc.Chrome()
        self.result = []
        self.flag_brand = False
        self.flag_start = True
        self.dynamic_api = ""
        self.total_pages = 0

    # Получаем список уникальных брендов из файла радуги

    def get_brands(self):
        data = pd.read_excel("../raduga.xlsx")
        return list(Counter(data["Бренд"].tolist()))

    # Проверяем API на адекватность - бывает поиск определяет бренд и из-за этого работа продолжается по другому API
    # В данном случае работа делится на self.dynamic_api - для брендов предсказанных поиском и self.api - для неопределенных

    def verify_api(self, page: int, brand: str):
        try:
            self.driver.get(self.api.format(page, page, brand))
            response = json.loads(self.driver.find_element(By.TAG_NAME, "pre").text)
            items = json.loads(list(response.get("widgetStates").values())[0]).get("items")

            # Делаем проверку на наличие в widgetStates данных в searchResultsV2 и сразу получаем первые данные
            if items:
                for item in items:
                    link = item.get("action").get("link")
                    # stock = item.get("multiButton").get("ozonButton").get("addToCartButtonWithQuantity").get("maxItems") # Количество в наличии, хз надо или нет, убрал пока...
                    # Нужно делать проверку на наличие данного ключа, иначе ошибка
                    self.result.append(link)

                # На первой странице получаем количество страниц для парсинга
                self.total_pages = json.loads(response.get("shared")).get("catalog").get("totalPages")

            else:
                # Меняем значение флага для корректного перехода вэбдрайвера по ссылке в get_links_from_page
                self.flag_brand = True

                # Вводится новая переменная self.api_brand
                # При переходе на данную ссылку api автоматом поставляет валидную ссылку, которую мы дальше будем искать в объекте
                # Это необходимо, т.к. предугадать ID бренда, который используется в ссылке, другим способом не знаю как)))

                self.driver.get(self.api_brand.format(brand))
                response = json.loads(self.driver.find_element(By.TAG_NAME, "pre").text)

                # На первой странице получаем количество страниц для парсинга
                self.total_pages = json.loads(response.get("shared")).get("catalog").get("totalPages")

                widgets = response.get("widgetStates")
                pattern = re.compile(r'megaPaginator')
                pattern_v2 = re.compile(r'searchResultsV2')

                # Находим ссылку на следующую страницу и форматируем её - БУДЕТ ОШИБКА ЕСЛИ СТРАНИЦА 1 - надо получить такой бренд, чтобы фиксануть код
                for widget in widgets:
                    if re.search(pattern, widget):
                        default_url = "https://www.ozon.ru/api/composer-api.bx/page/json/v2?url="
                        url_request = json.loads(widgets.get(widget)).get("nextPage").replace("layout_page_index=2", "layout_page_index={}").replace("page=2", "page={}")
                        self.dynamic_api = default_url + url_request
                        break

                for widget in widgets:
                    if re.search(pattern_v2, widget):
                        for item in json.loads(widgets.get(widget)).get("items"):
                            link = item.get("action").get("link")
                            self.result.append(link)

        except NoSuchElementException as e:
            self.flag_start = False
            logging.warning(f'Ошибка! Нет элемента - {e}')

        finally:
            logging.info("Проверка API прошла!")


    def get_links_from_page(self, page: int, brand: str):
        try:
            self.driver.get(self.dynamic_api.format(page, page)) if self.flag_brand else self.driver.get(self.api.format(page, page, brand))

            response = json.loads(self.driver.find_element(By.TAG_NAME, "pre").text)
            items = json.loads(list(response.get("widgetStates").values())[0]).get("items")


            for item in items:
                link = item.get("action").get("link")
                # stock = item.get("multiButton").get("ozonButton").get("addToCartButtonWithQuantity").get("maxItems") # Количество в наличии, хз надо или нет, убрал пока...
                # Нужно делать проверку на наличие данного ключа, иначе ошибка
                self.result.append(link)

        except NoSuchElementException as e:
            logging.warning(f'Ошибка! Нет элемента - {e}')

        finally:
            # На последней странице делаем сброс настроек
            if page == self.total_pages:
                self.flag_brand = False
                self.total_pages = 0
                self.dynamic_api = ""


    # Сохраняем данные по каждому бренду в отдельности
    def save_result(self, result, brand):
        today = str(datetime.date.today())
        date = datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S')
        data = {
            "brand": brand,
            "links": result
        }
        path = "./results/" + date
        if not os.path.exists(path):
            os.makedirs(path + "/items")
            os.makedirs(path + "/links")

        with open(f'results/{today}/links/{brand}_links_{date}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def parse(self, brand: str):
        self.result = []
        self.verify_api(1, brand)

        if self.flag_start:
            for i in range(2, self.total_pages + 1):
                self.get_links_from_page(i, brand)
                time.sleep(0.5)

            self.save_result(self.result, brand)
        elif len(self.result) != 0:
            self.save_result(self.result, brand)

        self.flag_start = True

    def start_parser(self):
        brands = self.get_brands()
        for brand in brands[5:]:
            self.parse(brand)


if __name__ == '__main__':
    # SpiderGetLinksSearch().start_parser()
    print(SpiderGetLinksSearch().get_brands())