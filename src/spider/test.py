import pandas as pd
import datetime
import os
import logging
import undetected_chromedriver as uc
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re
from threading import *
import time


class SpiderRadugaFile:
    def __init__(self):
        self.data = None
        self.driver = None
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
        self.threads = 4
        self.dict_none = {}
        self.result_col = {}
        self.own_dict = []

    def start_parse(self, region: int, index: int, data):
        logging.info("*** Начинаем работу по получению цен ***")
        self.data = data
        self.thread_file(index, region)
        logging.info("*** Все успешно ***")
        return self.own_dict

    def thread_file(self, index, region):
        counter = 1
        for name in [i for i in self.data.columns[5:]]:
            self.result_col = {}
            logging.info("Обрабатываем URL с {} столбца".format(counter))
            counter += 1
            dict_links = self.get_arr_links(name, index)
            self.parse(dict_links[f"thread_{index}"], region)

            self.own_dict.append({
                "name": name,
                "results": self.result_col,
                "none": self.dict_none
            })

    def select_region(self, number: int):
        for item in self.region_dict:
            if item["number"] == number:
                self.url_chg_region += item["link"]
                logging.info("*** Выбрали регион: {} ***".format(item["region"]))
        # Меняем регион
        self.driver.get(self.url_chg_region)

    def get_arr_links(self, name: str, index: int):
        data = self.data[name].tolist()
        dict_links = {}
        dict_none = {}

        for i in range(len(data)):
            if type(data[i]) == str:
                dict_links[f"{i}"] = data[i]
            else:
                dict_none[f"{i}"] = " "

        dicts = {}

        for j in range(self.threads):
            dicts[f"thread_{j}"] = {}
            for key, value in list(dict_links.items())[j::self.threads]:
                dicts[f"thread_{j}"].update({key: value})
            if index == j:
                for key, value in list(dict_none.items())[j::self.threads]:
                    self.dict_none.update({key: value})

        return dicts

    def parse(self, dicts, region):
        self.driver = uc.Chrome()

        self.select_region(region)
        time.sleep(0.5)

        obj_prices = {}

        for index, link in dicts.items():
            url = f'{self.api + link}'  # .replace("https://www.ozon.ru", "")
            # Идем по ссылке
            logging.info("Получаем данные с - {}".format(link))

            try:
                # Ставим ожидание загрузки страницы не более 3 секунд
                self.driver.set_page_load_timeout(7)

                self.driver.get(url)
                response = self.driver.find_element(By.TAG_NAME, "pre").text
                time.sleep(0.5)

            except (NoSuchElementException, TimeoutException) as e:
                logging.warning(f'Ошибка! {e.msg}')
                self.driver.quit()
                time.sleep(7)
                self.driver = uc.Chrome()
                # Ставим ожидание загрузки страницы не более 3 секунд
                self.driver.set_page_load_timeout(7)
                # Меняем регион
                self.driver.get(self.url_chg_region)
                # Идем по ссылке
                self.driver.get(url)
                response = self.driver.find_element(By.TAG_NAME, "pre").text

            try:
                data = json.loads(response)
                widgets = data.get('widgetStates')
                price = " "
                discount_price = None
                title = None
                brand = None
                category = None
                sku = None
                url = None
                description = None

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
                            discount_price = re.search(r'[0-9]+', prices.get('originalPrice').replace(u'\u2009', ''))[0]
                        else:
                            discount_price = 0

                layout = json.loads(data.get('layoutTrackingInfo'))

                if layout.get('brandName'):
                    brand = layout.get('brandName')

                if layout.get('categoryName'):
                    category = layout.get('categoryName')

                if layout.get('sku'):
                    sku = layout.get('sku')

                if layout.get('currentPageUrl'):
                    url = layout.get('currentPageUrl')

                if json.loads(data.get('seo').get('script')[0].get('innerHTML')).get('description'):
                    description = json.loads(data.get('seo').get('script')[0].get('innerHTML')).get('description')

                product = {
                    "title": title,
                    "price": price,
                    "discount_price": discount_price,
                    "brand": brand,
                    "category": category,
                    "description": description,
                    "sku": sku,
                    "url": url
                }

                price = '=HYPERLINK("%s", "%s")' % (link, price)

                self.save_update_json(product, region)
                obj_prices.update({index: price})


            except AttributeError as e:
                obj_prices.update({index: " "})
                logging.warning("Ошибка! {}".format(e))

            except TypeError:
                obj_prices.update({index: " "})
                logging.warning("Итерация по NoneType")

            finally:
                logging.info("Получение данных по ссылке завершено.")

        self.result_col.update(obj_prices)
        return obj_prices

    def save_update_json(self, product, region):
        today = str(datetime.date.today())
        path = "./results/" + today + "/items"
        if not os.path.exists(path):
            os.makedirs(path)

        with open("./results/{}/items/region_{}_raduga_SKU.json".format(today, region), "r+", encoding='utf-8') as f:
            data = json.load(f)
            data.append(product)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)

class StartAndSaveParser:
    def __init__(self):
        self.data = None
        self.thread_info = []
        self.arr_name = []
        self.arr_links = []
        self.arr_none = []

    def get_data(self, path: str):
        df = pd.read_excel(path)
        data = pd.DataFrame(df.drop([i for i in df.columns[5:] if "www.ozon.ru" not in i], axis=1))
        return data

    def mystart_parse(self, region, index, data):
        pices_dict = SpiderRadugaFile().start_parse(region, index, data)
        self.thread_info.append(pices_dict)

    def thread_start(self, path: str, region):
        data = self.get_data(path)
        threads = []
        for i in range(4):
            thread = Thread(
                target=self.mystart_parse,
                args=[region, i, data]
            )
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        self.convert_data()
        self.set_col_frame()
        self.save_file(self.data, region)

    def convert_data(self):
        for item in self.thread_info:
            for i in range(len(item)):
                if item[i]["name"] not in self.arr_name:
                    self.arr_name.append(item[i]["name"])
                if not self.arr_links[i]:
                    self.arr_links.append(item[i]["results"])
                else:
                    self.arr_links[i].update(item[i]["results"])
                if not self.arr_none[i]:
                    self.arr_none.append(item[i]["none"])
                else:
                    self.arr_none[i].update(item[i]["none"])


    def set_col_frame(self):
        for i in range(len(self.arr_name)):
            index = self.data.columns.get_loc(self.arr_name[i])
            full_res = {**self.arr_links[i], **self.arr_none[i]}
            full_res = dict(sorted(full_res.items()))
            arr = []

            for key, value in full_res.items():
                arr.append(value)

            self.data.insert(index, "Цена, ₽", arr, True)

    def save_file(self, results, region):
        today = str(datetime.date.today())
        date = datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S')
        path = "./results/" + today
        if not os.path.exists(path):
            os.makedirs(path + "/xlsxURL")

        results.to_excel("./results/{}/xlsxURL/{}_region_{}_raduga_SKU.xlsx".format(today, date, region),
                         encoding='utf-8', index=False, sheet_name="{}_Ozon".format(today))


if __name__ == "__main__":
    StartAndSaveParser().thread_start("../raduga1.xlsx", 2)