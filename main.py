from data_curl import cookies, headers
import requests
import os
import json
import math
import csv
import time
import random
from collections import Counter

"""
Соберу данные с сайта
https://re-store.ru/apple-iphone/?page=1

Алгоритм:
-из первого запроса получаю количество смартфонов и вычисляю количество страниц
-делаю запрос к каждой странице, достаю инфу и сохраняю в переменную
-записываю данные в json & csv

Почему находит 87 смартфонов, а в json86 ????
"""


def get_data(cookies=cookies , headers=headers):
    
    # все запросы в одной ссесии
    sess = requests.Session()
    
    data = {
        'action': 'get_catalog',
        'VUE': 'Y',
        'DDL': 'Y',
        'page': '1',
        'url': '/apple-iphone/?page=1',
    }
    
    response = sess.post('https://re-store.ru/cat/ajax.php', cookies=cookies, headers=headers, data=data).json()
    
    # создаю директорию для сохранения
    if not os.path.exists("data"):
        os.mkdir("data")    
   
    # пагинация
    # общее количество смартфонов (если покапаться, поглубже, то можно найти фрагмент, где уже есть это число, но я вычисляю методом деления)
    amount_smartphones = response.get("info").get("count")
    
    # вычисляю количество страниц (на одной странице 30 смартфонов) и округляю вверх
    last_page = math.ceil(amount_smartphones / 30)
    
    # инфоблог
    print(f"[info] found: smartphones:{amount_smartphones}, pages:{last_page}\n")
    
    # в этот словарь буду сохранять собранные данные для записи в json
    all_data_product = {}
    
    # в эту переменную буду сохранять данные для записи в csv
    all_data = []
    my_list = []
    
    # имя page, что бы не сохранять новую переменную
    for page in range(1, last_page + 1):
    # for page in range(3, 4):
        page = page
    
        # в значение 'page' подставлю свою переменную  
        data = {
            'action': 'get_catalog',
            'VUE': 'Y',
            'DDL': 'Y',
            'page': page,
            'url': '/apple-iphone/?page=1',
        }
    
        # делаю запрос к каждой странице (cookies & headers страрые, в data меняется 'page')
        response = sess.post('https://re-store.ru/cat/ajax.php', cookies=cookies, headers=headers, data=data).json()
            
        # достаю только нужную информацию о смартфонах
        product_from_page = response.get("products")
        
        for product in product_from_page:
            id = product.get("id")
            model = product.get("name")
            price = product.get("prices").get("current")
            price_old = product.get("prices").get("old")         
            link = f'https://re-store.ru{product.get("link")}'
            
            # print(f"{model}\n {price}\n {price_old}\n {link}\n{20 * '*'} ")
            
            # сохраняю данные для записи в csv
            all_data.append(
                [
                    model,
                    price,
                    price_old,
                    link
                ]
            )
            
            # сохраняю полученную инфу в переменную для записи в json
            # all_data_product[model] = { # это было изначально, но выяснилось, что 'model'-не уникальна, поэтому в ключ (json) добавлю 'id'
            all_data_product[f'{model} - {id}'] = {  # ключ = 'model-id'
                "price": price,
                "price_old": price_old,
                "link": link
            }

            my_list.append(model)
            
        # инфоблок
        print(f"[info] completed page:{page}\n")
        # пауза между запросами
        time.sleep(random.randrange(1, 3))
    
    # # сравниваю длину csv & json
    # print(len(all_data))
    # print(len(all_data_product))
    
    # поиск , какое из 'model' встречается несколько раз
    counter = Counter(my_list)
    print(counter)
    
    # записываю инфу в csv
    with open("data/all_data.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(  # записал шаблон
            (
                "model",
                "price",
                "price_old",
                "link"
            )
        )
        writer.writerows(all_data)
         
    # записываю словарь с полученной инфой в json
    with open("data/all_data_product.json", "w") as file:
        json.dump(all_data_product, file, indent=4, ensure_ascii=False)
    
    # инфоблок
    print(f"[info] information collection completed! ")
        

def main():
    get_data(cookies=cookies , headers=headers)
    
    
if __name__ == "__main__":
    main()
