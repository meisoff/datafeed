import json
import codecs
import scrapy

base = json.load(codecs.open("C:\ProgramData\Anaconda3\envs\parsing_data_feed\parsing_data_feed\spiders\/base_sellers.json", 'r', 'utf-8-sig'))
email = ["https://" + base[i]["url"] for i in range(3600, 3885)] # Менял периодичность из-за лага Scrapy - парсил 400 ссылок и ломался

class MailfinderSpider(scrapy.Spider):
    name = 'mailfinder'
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        }


    start_urls = email
    index = 3599 # Тут необходимо менять индекс, чтобы он корректно записывался. Он должен быть меньше на 1 ед. от нижней границы range

    def parse(self, response):
        res = response.css("a[href^=mailto]::attr(href)").get() if response.css("a[href^=mailto]").get() else None
        self.index += 1
        if res:
            yield {
                "index": self.index,
                "name": base[self.index]["name"],
                "email": res.replace("mailto:", ""),
                "url": base[self.index]["url"]
            }