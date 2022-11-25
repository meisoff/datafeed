import time
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
import json

class SpiderGetLinks:
    def __init__(self):
        self.driver = uc.Chrome(executable_path=r"../chromedriver.exe")
        self.url = "https://www.ozon.ru/category/kofemashiny-dlya-molotogo-kofe-31660/"
        self.api = "https://api.ozon.ru/composer-api.bx/page/json/v1?url=%2Fcategory%2F{}%2F%3Flayout_container%3Ddefault%26layout_page_index%3D{}%26page%3D{}"
        self.result = []

    def valid_category(self):
        link = self.url
        spltd_link = link.split("/")
        # Наличие или отсутствие / в конце ссылки
        category = spltd_link[-1] if spltd_link[-1] else spltd_link[-2]
        return category

    def start_request(self):
        res = {
            "links": []
        }

        for i in range(2, 6): # НЕОБХОДИМО СЧИТАТЬ MAX_PAGE

            with self.driver:
                self.driver.get(self.api.format(self.valid_category(), i, i))
                time.sleep(0.5)

            data = json.loads(self.driver.find_element(By.TAG_NAME, "pre").text)

            items = list(data["catalog"]["searchResultsV2"].values())[0]["items"]

            for item in items:
                url = item["action"]["link"]
                res["links"].append(url)

        with open('data_link.json', 'w') as f:
            json.dump(res, f, indent=4)





if __name__ == '__main__':
    SpiderGetLinks().start_request()