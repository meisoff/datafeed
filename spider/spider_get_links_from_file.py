import pandas as pd
import datetime
import os
import logging
import undetected_chromedriver as uc
import time
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re

class SpiderRadugaFile:
    def __init__(self):
        self.data = None
        self.driver = uc.Chrome(executable_path=r"../chromedriver.exe")
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

    def start_parse(self, path: str, region: int):
        logging.info("*** Начинаем работу по получению цен ***")
        self.data = self.get_data(path)
        self.select_region(region)
        counter = 1
        for name in [i for i in self.data.columns[5:]]:
            logging.info("Обрабатываем URL с {} столбца".format(counter))
            counter += 1
            arr_links = self.get_arr_links(name)
            arr_prices = self.parse(arr_links)
            self.set_col_frame(name, arr_prices)
        self.save_file(self.data, region)
        logging.info("*** Все успешно, всем спасибо! ***")


    def get_data(self, path):
        df = pd.read_excel(path)
        data = pd.DataFrame(df.drop([i for i in df.columns[5:] if "www.ozon.ru" not in i], axis=1))
        return data

    def select_region(self, number: int):
        for item in self.region_dict:
            if item["number"] == number:
                self.url_chg_region += item["link"]
                logging.info("*** Выбрали регион: {} ***".format(item["region"]))
        # Меняем регион
        self.driver.get(self.url_chg_region)

    def get_arr_links(self, name: str):
        return self.data[name].tolist()

    def parse(self, links):
        arr_prices = []
        for link in links:
            # Проверка на nan
            if type(link) == str:
                url = f'{self.api + link}'  #.replace("https://www.ozon.ru", "")
                # Идем по ссылке
                logging.info("Получаем данные с - {}".format(link))

                try:
                    # Ставим ожидание загрузки страницы не более 20 секунд
                    self.driver.set_page_load_timeout(20)

                    self.driver.get(url)
                    response = self.driver.find_element(By.TAG_NAME, "pre").text
                    time.sleep(0.5)

                except (NoSuchElementException, TimeoutException) as e:
                    logging.warning(f'Ошибка! {e.msg}')
                    self.driver.quit()
                    time.sleep(10)
                    self.driver = uc.Chrome()
                    # Ставим ожидание загрузки страницы не более 20 секунд
                    self.driver.set_page_load_timeout(20)
                    # Меняем регион
                    self.driver.get(self.url_chg_region)
                    # Идем по ссылке
                    self.driver.get(url)
                    response = self.driver.find_element(By.TAG_NAME, "pre").text

                try:
                    data = json.loads(response)
                    widgets = data.get('widgetStates')
                    price = " "
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

                    arr_prices.append(price)

                except AttributeError as e:
                    arr_prices.append(" ")
                    logging.warning("Ошибка! {}".format(e))

                except TypeError:
                    arr_prices.append(" ")
                    logging.warning("Итерация по NoneType")

                finally:
                    logging.info("Получение данных по ссылке завершено.")
            else:
                arr_prices.append(" ")
        return arr_prices

    def set_col_frame(self, name: str, arr):
        index = self.data.columns.get_loc(name)
        self.data.insert(index + 1, "Цена, ₽", arr, True)

    def save_file(self, results, region):
        today = str(datetime.date.today())
        date = datetime.datetime.now().strftime('%Y-%m-%d__%H-%M')
        path = "./results/" + today
        if not os.path.exists(path):
            os.makedirs(path + "/xlsxURL")

        results.to_excel("./results/{}/xlsxURL/{}_region_{}_raduga_SKU.xlsx".format(today, date, region),
                         encoding='utf-8', index=False, sheet_name="{}_Ozon".format(today))

if __name__ == "__main__":
    SpiderRadugaFile().start_parse("../raduga.xlsx", 2)


