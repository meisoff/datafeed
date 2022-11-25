import time
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
import re
import datetime
import os
import logging


class SpiderGetInfo:
    def __init__(self):
        self.driver = uc.Chrome(executable_path=r"../chromedriver.exe")
        self.api = "https://www.ozon.ru/api/composer-api.bx/page/json/v2?url="
        self.result = []
        self.brand = ""

    def get_count_items(self, dir_date):
        count = 0
        path = "./results/{}/items".format(dir_date)
        for item in os.listdir(path):
            with open(f"{path}/{item}", "r", encoding="UTF-8") as f:
                data = json.load(f)
                count += len(data)
        print("Количество полученных товаров с поиска по бренду - {} эл.".format(count))

    def read_links(self, file):
        # ссылку на файл с ссылками
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_info(self, file):
        links = self.read_links(file)
        self.brand = links["brand"]
        for link in links["links"]:
            # # Используем если парсили ссылки по html
            # url = f'{self.api + link.replace("https://www.ozon.ru", "")}'

            # Используем если парсили ссылки по API
            url = f'{self.api + link}'
            self.driver.get(url)

            try:
                response = self.driver.find_element(By.TAG_NAME, "pre").text
                time.sleep(0.5)
                data = json.loads(response)

                widgets = data.get('widgetStates')
                for key, value in widgets.items():
                    if 'webProductHeading' in key:
                        title = json.loads(value).get('title')
                    if 'webSale' in key:
                        prices = json.loads(value).get('offers')[0]
                        if prices.get('price'):
                            price = re.search(r'[0-9]+', prices.get('price').replace(u'\u2009', ''))[0]
                        else:
                            price = 0
                        if prices.get('originalPrice'):
                            discount_price = re.search(r'[0-9]+', prices.get('originalPrice').replace(u'\u2009', ''))[0]
                        else:
                            discount_price = 0

                layout = json.loads(data.get('layoutTrackingInfo'))
                brand = layout.get('brandName')
                category = layout.get('categoryName')
                sku = layout.get('sku')
                url = layout.get('currentPageUrl')

                product = {
                    'title': title,
                    'price': price,
                    'discount_price': discount_price,
                    'brand': brand,
                    'category': category,
                    'sku': sku,
                    'url': url
                }
                self.result.append(product)

            except NoSuchElementException as e:
                logging.warning(f'Ошибка! Нет элемента - {e.msg}')

            except AttributeError:
                pass

            except TypeError:
                logging.warning(f'Итерация по NoneType')

            finally:
                logging.info(f"Получение данных по ссылке завершено. URl - {link}")

        # ПАПКА С ДАТОЙ СОЗДАЕТСЯ САМА
        date = str(datetime.date.today())

        with open(f'./results/{date}/items/{self.brand}_items_{datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S")}.json', 'w', encoding='utf-8') as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # for item in os.listdir("./results/2022-10-20/links")[2:]:
    #     SpiderGetInfo().get_info("./results/2022-10-20/links" + "/" + item)
    SpiderGetInfo().get_count_items("2022-10-20")