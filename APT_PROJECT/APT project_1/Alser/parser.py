from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import csv

HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
         'accept' : '*/*'}

HOST = 'https://alser.kz'
HOST_URL = "https://alser.kz/c/vse-smartfony"


def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def pagination(html):
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        div = soup.find('div', class_='pagination catalog-pagination')
        li = div.find_all('li')
        page = li[len(li)-2].get_text()
        return int(page.strip())


def get_url_items(url):
    html = get_html(url)
    if html.status_code == 200:
        page_number = pagination(html)
        file = open('item_urls.txt', mode='w', encoding='utf-8')
        for page in range(page_number+1):
            html = get_html(f"{url}/page-{page}")
            soup = BeautifulSoup(html.text, 'html.parser')
            div = soup.find_all('div', class_='product-item__front')
            for item in div:
                u = item.find('a', class_='product-item__image').get('href')
                file.write(f"{HOST}{u}\n")


def save_csv(data):
    with open('alser_sm_dataset.csv', encoding='utf-8', mode='a', newline="") as file:
        writer = csv.writer(file)
        writer.writerow([data['title'],
                         data['price'],
                         data['operating_system'],
                         data['display_diagonal'],
                         data['memory'],
                         data['main_camera'],
                         data['front_camera'],
                         data['delivery'],
                         data['manufacturer'],
                         data['features'],
                         data['color']
                         ])


def get_content_items(url):
    html = get_html(f"{url}#collapse38")
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        try:
            title = soup.find('div', class_='detail-info__name').get_text().strip()
        except:
            title = None
        try:
            price = int(''.join(soup.find('div', class_='price').get_text().strip().split()))
        except:
            price = None

        div = soup.find('div', class_='general-specs__rows').find_all('div', class_='row')
        operating_system = ''
        display_diagonal = ''
        memory = ''
        features = ''
        for item in div:
            column_name = item.find('div', class_='col-md-8').get_text().strip()
            if column_name == 'Операционная система':
                operating_system = item.find('div', class_='col-md-4').get_text().strip()
            elif column_name == 'Диагональ':
                display_diagonal = item.find('div', class_='col-md-4').get_text().strip()
            elif column_name == 'Объем встроенной памяти':
                memory = ''.join(item.find('div', class_='col-md-4').get_text().strip().split())
            else:
                if column_name == 'Технология изготовления экрана':
                    features += column_name + ":" + item.find('div', class_='col-md-4').get_text().strip().split('\n')[0] + ', '
                else:
                    features += column_name+":"+item.find('div', class_='col-md-4').get_text().strip()+', '

        div2 = soup.find('div', id='collapse31').find('div', class_='panel-body').find_all('div', class_="row")
        manufacturer = ''
        color = ''
        for item in div2:
            column_name = item.find_all('div', class_='col-md-4')
            if column_name[0].get_text().strip() == 'Производитель':
                manufacturer = column_name[1].get_text().strip()
            elif column_name[0].get_text().strip() == 'Цвет задней панели':
                color = column_name[1].get_text().strip()
            else:
                features += column_name[0].get_text().strip() + ":" + column_name[1].get_text().strip() + ', '

        div3 = soup.find('div', id='collapse38').find('div', class_='panel-body').find_all('div', class_="row")
        main_camera = ''
        front_camera = ''
        for item in div3:
            column_name = item.find_all('div', class_='col-md-4')
            if column_name[0].get_text().strip() == 'Количество мегапикселей основной камеры (Мп)':
                main_camera = column_name[1].get_text().strip()
            elif column_name[0].get_text().strip() == 'Количество мегапикселей фронтальной камеры (Мп)':
                front_camera = column_name[1].get_text().strip()
            else:
                features += column_name[0].get_text().strip() + ":" + column_name[1].get_text().strip() + ', '

        delivery = 'бесплатно' if price > 10000 else 'доставка платная'
        data = {'title': title,
                'price': price,
                'operating_system': operating_system,
                'display_diagonal': display_diagonal,
                'memory': memory,
                'main_camera': main_camera,
                'front_camera': front_camera,
                'delivery': delivery,
                'manufacturer': manufacturer,
                'features': features,
                'color': color
                }
        print(data)
        save_csv(data)


# print(pagination(get_html(HOST_URL)))

####### Parsing urls of sm ##################
#get_url_items(HOST_URL)

# get_content_items('https://alser.kz/p/galaxy-z-flip-3-new128gb-green')

####### Parsing alser sm content ##################
with open('item_urls.txt', encoding='utf-8', mode='r') as data_file:
    with ThreadPoolExecutor(max_workers=5) as executor:
        t1 = [executor.submit(get_content_items, row.strip()) for row in data_file]
















