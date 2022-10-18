import time
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
import json
import re


class SpiderGetInfo:
    def __init__(self):
        self.driver = uc.Chrome(executable_path=r"../chromedriver.exe")
        self.api = "https://www.ozon.ru/api/composer-api.bx/page/json/v2?url="
        self.result = []

    def read_links(self):
        with open('result.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_info(self):
        links = self.read_links()
        for link in links["links"]:
            url = f'{self.api + link.replace("https://www.ozon.ru", "")}'

            self.driver.get(url)
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

        with open('res.json', 'w', encoding='utf-8') as f:
            f.write(str(self.result))


if __name__ == '__main__':
    SpiderGetInfo().get_info()