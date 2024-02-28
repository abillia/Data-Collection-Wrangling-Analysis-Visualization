import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'accept': '*/*'}
HOST = "https://kaspi.kz/shop/"
URL = "https://kaspi.kz/shop/c/smartphones/class-samsung-galaxy/?at=1&page={0}"


def get_content_by_url(url):
    driver = webdriver.Chrome(executable_path="/Users/nursbrat/PycharmProjects/chromedriver")
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')
    driver.quit()
    return soup


def get_items_by_pagination():
    pages_count = 100
    for page in range(1, pages_count + 1):
        soup = get_content_by_url(URL.format(page))
        save_file(get_names(soup), get_prices(soup), get_link_each_item(soup))


def get_names(soup):
    names = []
    for name in soup.findAll('a', attrs={'class': "item-card__name-link"}):
        if name not in names:
            names.append(name.text)
    return names


def get_link_each_item(soup):
    links = []
    for url in soup.find_all('a', attrs={'class': "item-card__name-link"}, href=True):
        if url not in links:
            links.append(url['href'])
    return links


def get_prices(soup):
    prices = []
    for price in soup.findAll('span', attrs={'class': "item-card__prices-price"}):
        if price not in prices:
            prices.append(price.text)
    return prices


def save_file(names, prices, links):
    file = open("kaspi_store_dataset.csv", encoding='utf-8', mode='a', newline="")
    fieldnames = ['Title', 'Url']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    for i, j, k in zip(range(len(names)), range(len(prices)), range(len(links))):
        writer.writerow({"Title": names[i], "Url": links[k]})
    file.close()


def get_item_content(url):
    soup = get_content_by_url(url)
    try:
        name = soup.select('h1.item__heading')[0].text.strip()
    except:
        name = None
    try:
        price = soup.select('div.item__price-once')[0].text.strip()
    except:
        price = None
    try:
        item_price_month = soup.select('div.item__price-month')[0].text.strip()
    except:
        item_price_month = None
    try:
        operating_system = find_list_by_name(soup, 'Операционная система')[0].find('dd').text
    except:
        operating_system = None
    try:
        display_diagonal = find_list_by_name(soup, 'Диагональ')[0].find('dd').text.strip()
    except:
        display_diagonal = None
    try:
        model = find_list_by_name(soup, 'Модель процессора')[0].find('dd').text.strip()
    except:
        model = None
    try:
        memory = find_list_by_name(soup, 'Объем встроенной памяти')[0].find('dd').text.strip()
    except:
        memory = None
    try:
        main_camera = find_list_by_name(soup, 'Фотокамера')[0].find('dd').text.strip()
    except:
        main_camera = None
    try:
        front_camera = find_list_by_name(soup, 'Фронтальная камера')[0].find('dd').text.strip()
    except:
        front_camera = None
    try:
        color = find_list_by_name(soup, 'Цвет')[0].find('dd').text.strip()
    except:
        color = None
    try:
        battery = find_list_by_name(soup, 'Емкость аккумулятора')[0].find('dd').text.strip()
    except:
        battery = None
    try:
        weight = find_list_by_name(soup, 'Вес')[0].find('dd').text.strip()
    except:
        weight = None
    try:
        features = find_list_by_name(soup, 'Особенности')[0].find('dd').text.strip()
    except:
        features = 'Нет'

    content = {'title': name,
               'price': price,
               'Item price month': item_price_month,
               'operating_system': operating_system,
               'display_diagonal': display_diagonal,
               'memory': memory,
               'main_camera': main_camera,
               'front_camera': front_camera,
               'model': model,
               'color': color,
               'battery': battery,
               'weight': weight,
               'features': features
               }
    save_csv(content, "kaspi_store_item_content_dataset.csv")


def find_list_by_name(soup, name):
    return soup.find_all(
        lambda t: t.name == 'dl' and name in t.select('dt.specifications-list__spec-term')[0].text)


def save_csv(content, name_csv):
    with open(name_csv, encoding='utf-8', mode='a', newline="") as file:
        writer = csv.writer(file)
        writer.writerow([content['title'],
                         content['price'],
                         content['Item price month'],
                         content['operating_system'],
                         content['display_diagonal'],
                         content['memory'],
                         content['main_camera'],
                         content['front_camera'],
                         content['model'],
                         content['color'],
                         content['battery'],
                         content['weight'],
                         content['features']
                         ])


# def truncate_csv_file_first():
#     file = open("kaspi_store_dataset.csv", encoding='utf-8', mode='w', newline="")
#     file.close()
#     get_items_by_pagination()

with open('kaspi_sm_dataset.csv') as sample, open('phones_with_longest_battery_life.csv', "w") as out:
    csv1 = csv.reader(sample)
    header = next(csv1, None)
    csv_writer = csv.writer(out)
    if header:
        csv_writer.writerow(header)
    csv_writer.writerows(sorted(csv1, key=lambda x:int(x[9])))



# with open("kaspi_store_dataset.csv", encoding='utf-8') as data_file:
#     file = open("kaspi_store_item_content_dataset.csv", encoding='utf-8', mode='w', newline="")
#     file.close()
#     data = csv.reader(data_file)
#     with ThreadPoolExecutor(max_workers=1) as executor:
#         t1 = [executor.submit(get_item_content, row[1]) for row in data]

# truncate_csv_file_first()
