from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests
import csv

HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36', 'accept' : '*/*'}

HOST = 'https://shop.kz'
HOST_URL = "https://shop.kz/smartfony/filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/"


def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def pagination(html):
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        div = soup.find('div', class_='bx-pagination bx-blue')
        li = div.find_all('li')
        page = li[len(li)-2].get_text()
        return int(page.strip())


def get_url_items(url):
    html = get_html(url)
    if html.status_code == 200:
        page_number = pagination(html)
        file = open('items_url.txt', mode='w', encoding='utf-8')
        for page in range(page_number+1):
            html = get_html(f"{url}/?PAGEN_1={page}")
            soup = BeautifulSoup(html.text, 'html.parser')
            div = soup.find_all('div', class_='bx_catalog_item_container gtm-impression-product')
            for item in div:
                u = item.find('a', class_='bx_catalog_item_images_double').get('href')
                file.write(f"{HOST}{u}\n")


def save_csv(data):
    with open('shop_dataset.csv', encoding='utf-8', mode='a', newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            data['title'],
            data['price'],
            data['operating_system'],
            data['display_diagonal'],
            data['memory'],
            data['main_camera'],
            data['front_camera'],
            data['manufacturer'],
            data['features'],
            data['color']
        ])


def get_content_items(url):
    html = get_html(url)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        try:
            title = soup.find('h1', class_='bx-title dbg_title').get_text().strip()
        except:
            title = None
        try:
            price = (''.join(soup.find('div', class_='item_current_price').get_text().strip().split()))
        except:
            price = None

        div = soup.find('dl', class_='bx_detail_chars').find_all('div', class_='bx_detail_chars_i')

        operating_system = ''
        display_diagonal = ''
        memory = ''
        main_camera = ''
        front_camera = ''
        manufacturer = ''
        features = ''
        color = ''

        for item in div:
            column_name = item.find('dt', class_='bx_detail_chars_i_title').get_text().strip()
            if column_name == 'Операционная система':
                operating_system = item.find('dd', class_='bx_detail_chars_i_field').get_text().strip()
            elif column_name == 'Размер экрана, дюйм':
                display_diagonal = item.find('dd', class_='bx_detail_chars_i_field').get_text().strip()
            elif column_name == 'Объем встроенной памяти':
                memory = item.find('dd', class_='bx_detail_chars_i_field').get_text().strip()
            elif column_name == 'Основная камера, Мп':
                main_camera = item.find('dd', class_='bx_detail_chars_i_field').get_text().strip()
            elif column_name == 'Фронтальная камера, Мп':
                front_camera = item.find('dd', class_='bx_detail_chars_i_field').get_text().strip()
            elif column_name == 'Производитель':
                manufacturer = item.find('dd', class_='bx_detail_chars_i_field').get_text().strip()
            elif column_name == 'Цвет, используемый в оформлении':
                color = item.find('dd', class_='bx_detail_chars_i_field').get_text().strip()
            else: 
                if column_name == 'Стекло экрана':
                    features = item.find('dd', class_='bx_detail_chars_i_field').get_text().strip()
                    print(features)

        data = {
            'title': title,
            'price': price,
            'operating_system': operating_system,
            'display_diagonal': display_diagonal,
            'memory': memory,
            'main_camera': main_camera,
            'front_camera': front_camera,
            'manufacturer': manufacturer,
            'features': features,
            'color': color
        }

        print(data)
        save_csv(data)


# print(pagination(get_html(HOST_URL)))

####### Parsing urls of sm ##################
# get_url_items(HOST_URL)

# get_content_items('https://shop.kz/offer/smartfon-xiaomi-mi-11-lite-5g-ne-8gb-128gb-bubblegum-blue-2109119dg/')

####### Parsing alser sm content ##################
with open('items_url.txt', encoding='utf-8', mode='r') as data_file:
    with ThreadPoolExecutor(max_workers=5) as executor:
        t1 = [executor.submit(get_content_items, row.strip()) for row in data_file]