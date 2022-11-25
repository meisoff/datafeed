import time
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
import json
import re
from bs4 import BeautifulSoup

class SpiderGetLinks:
    def __init__(self):
        self.driver = uc.Chrome(executable_path=r"../chromedriver.exe")
        self.url = "https://www.ozon.ru/category/kofemashiny-dlya-molotogo-kofe-31660/"
        self.api = "https://www.ozon.ru/api/composer-api.bx/page/json/v2?url="
        self.result = []

    def start_request(self):
        with self.driver:
            self.driver.get(self.url)
            time.sleep(0.5)

        prod = {
            "links": []
        }
        links = self.driver.find_elements(By.XPATH, value='//div[@class="widget-search-result-container kv"]/div/div/div/a')

        for link in links:
            prod["links"].append(link.get_attribute("href"))

        with open('util/result.json', 'w', encoding='utf-8') as f:
            f.write(str(prod))


if __name__ == '__main__':
    SpiderGetLinks().start_request()