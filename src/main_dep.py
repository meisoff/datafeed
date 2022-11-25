import os
import json

dir_date = "2022-10-24"
count = 0
path = "./spider/results/{}/links".format(dir_date)
for item in os.listdir(path):
    with open(f"{path}/{item}", "r", encoding="UTF-8") as f:
        data = json.load(f)
        for item in data:
            count += len(item["links"])
print("Количество полученных товаров с поиска по бренду - {} эл.".format(count))

if __name__ == '__main__':
    pass