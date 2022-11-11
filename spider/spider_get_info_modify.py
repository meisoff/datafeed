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

    def start_parser(self, date:str):
        path = f"./results/{date}/links"
        for item in os.listdir(path):
            self.get_info(path + "/" + item)
        # self.get_count_items(date)


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
        arr = self.read_links(file)
        count = 0

        for obj in arr:
            mid_res = None
            own_price = 99999999999

            self.brand = obj["name"]
            if len(obj["links"]) != 0:
                for link in obj["links"]:
                    url = f'{self.api + link}'
                    self.driver.get(url)

                    print(count)
                    count += 1

                    try:
                        response = self.driver.find_element(By.TAG_NAME, "pre").text
                        time.sleep(0.5)

                    except NoSuchElementException as e:
                        logging.warning(f'Ошибка! Нет элемента - {e.msg}')
                        self.driver.quit()
                        time.sleep(10)
                        self.driver = uc.Chrome()
                        self.driver.get(url)
                        response = self.driver.find_element(By.TAG_NAME, "pre").text

                    try:

                        data = json.loads(response)

                        widgets = data.get('widgetStates')
                        for key, value in widgets.items():
                            if 'webProductHeading' in key:
                                title = json.loads(value).get('title')
                            if 'webSale' in key:
                                if json.loads(value).get('offers'):
                                    prices = json.loads(value).get('offers')[0]
                                else:
                                    prices = json.loads(value).get('offer')

                                if prices.get('price'):
                                    price = re.search(r'[0-9]+', prices.get('price').replace(u'\u2009', ''))[0]
                                else:
                                    price = 0
                                if prices.get('originalPrice'):
                                    discount_price = \
                                    re.search(r'[0-9]+', prices.get('originalPrice').replace(u'\u2009', ''))[0]
                                else:
                                    discount_price = 0

                        layout = json.loads(data.get('layoutTrackingInfo'))
                        brand = layout.get('brandName')
                        category = layout.get('categoryName')
                        sku = layout.get('sku')
                        url = layout.get('currentPageUrl')

                        if int(price) != 0 and int(price) < own_price and brand in self.brand:
                            mid_res = {
                                'goodInfo': {
                                    'name': self.brand,
                                    'title': title,
                                    'price': price,
                                    'discount_price': discount_price,
                                    'brand': brand,
                                    'category': category,
                                    'sku': sku,
                                    'url': url
                                },
                                'errorCode': 0
                            }

                            own_price = int(price)
                    except AttributeError:
                        pass

                    except TypeError:
                        logging.warning(f'Итерация по NoneType')

                    finally:
                        logging.info(f"Получение данных по ссылке завершено. URl - {link}")
            else:
                mid_res = {
                    'goodInfo': {
                        'name': self.brand,
                    },
                    "errorCode": 1
                }

            self.result.append(mid_res)
            print(mid_res)

        # ПАПКА С ДАТОЙ СОЗДАЕТСЯ САМА
        date = str(datetime.date.today())

        with open(f'./results/{date}/items/excel_items_{datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S")}.json', 'w', encoding='utf-8') as f:
            json.dump(self.result, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # Format date to start %Y-%m-%d
    SpiderGetInfo().start_parser("2022-10-24")