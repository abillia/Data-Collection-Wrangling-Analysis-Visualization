from concurrent.futures import ThreadPoolExecutor
import requests
import csv
from bs4 import BeautifulSoup


HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
         'accept' : '*/*'}
HOST = "https://www.sulpak.kz"


def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response

# Gets urls of smartphones brands
def get_catalog(filename):
    html = get_html("https://www.sulpak.kz/p/sotoviye_telefoniy")
    if html.status_code == 200:
        file = open(filename, encoding='utf-8', mode='w')
        soup = BeautifulSoup(html.text, 'html.parser')
        urls_catalog = soup.find_all('div', class_="portal-menu-block manufacturer-block")[1].find_all('a')
        for url in urls_catalog:
            u = url.get('href')
            title = url.get_text().replace('\n', '')
            file.write(f"{title.strip()},{HOST}{u}\n")

# Parses urls of items page by page. Ans calls method get_url_items_content to get url of item
def get_url_items(url, city):
    html = get_html(url)
    if html.status_code == 200:
        pages_count = get_page_number(url)
        print(pages_count, city)
        for number in range(1, pages_count+1):
            html = get_html(url, params={'page': number})
            get_url_items_content(html)

# Parses url of item
def get_url_items_content(html):
    if html.status_code == 200:
        file = open("item_urls.csv", encoding='utf-8', mode='a', newline="")
        writer = csv.writer(file)
        writer.writerow(['Title', 'Url'])
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find('ul', class_='goods-container').find_all('div', class_='product-container-right-side')
        for item in items:
            a = item.find('a')
            url_item = a.get('href')
            title_item = a.get_text()
            writer.writerow([title_item.strip(), HOST+url_item.strip()])
            # print([title_item.strip(), SITE+url_item.strip()])
        file.close()

# Return number of pages of website
def get_page_number(url):
    html = get_html(url)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        item = soup.find('div', class_='pagination')
        if item:
            item = item.find('div', class_='pages-list')
            number = item.find_all('a')[-1].get_text()
            return int(number)
        else:
            return 1

# This part saves data to csv file
def save_csv(data):
    with open('sulpak_sm_dataset.csv', encoding='utf-8', mode='a', newline="") as file:
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
                         data['manufacturer_country'],
                         data['features'],
                         data['color']
                         ])


# This part for parsing content of items
def get_item_content(url, title):
    html = get_html(url)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        table = soup.find('div', class_='product-review-description').find('table').find_all('tr')
        try:
            price = soup.find('div', class_='current-price').get_text().split()
            price = int(price[0] + price[1])
        except:
            price = None

        try:
            color = soup.find('span', class_='ppr-color-value').get_text().strip()
        except:
            color = None

        try:
            operating_system = table[0].find_all('td')[1].get_text().strip()
        except:
            operating_system = None
        try:
            display_diagonal = table[2].find_all('td')[1].get_text().strip()
        except:
            display_diagonal =None
        try:
            memory = table[3].find_all('td')[1].get_text().strip()
        except:
            memory = None
        try:
            main_camera = table[4].find_all('td')[1].get_text().strip()
        except:
            main_camera = None
        try:
            front_camera = table[5].find_all('td')[1].get_text().strip()
        except:
            front_camera = None

        delivery = 'бесплатно' if price > 15000 else 'доставка платная'

        characteristic_url = url + "#characteristicsTab"
        html = get_html(characteristic_url)
        soup_ch = BeautifulSoup(html.text, 'html.parser')
        table_2=''
        try:
            div = soup_ch.find('div', class_='product-page-left-side').find_all('table')
            try:
                table_2 = div[0].find_all('td')
            except:
                table_2 = None
        except:
            div = None

        Manufacturer = None
        Manufacturer_country = None
        features = None
        if table_2:
            index = 0
            while index < len(table_2):
                text = table_2[index].get_text().strip()
                text = text.split(' ')[0].strip()
                if(text == 'Производитель'):
                    Manufacturer = table_2[index+1].get_text().strip()
                elif(text == 'Страна'):
                    Manufacturer_country = table_2[index+1].get_text().strip()
                elif(text == 'Особенности'):
                    features = table_2[index+1].get_text().strip()
                index = index+2

        data = {'title': title,
                'price': price,
                'operating_system': operating_system,
                'display_diagonal': display_diagonal,
                'memory': memory,
                'main_camera': main_camera,
                'front_camera': front_camera,
                'delivery': delivery,
                'manufacturer': Manufacturer,
                'manufacturer_country':Manufacturer_country,
                'features': features,
                'color':color
                }
        print(data)
        save_csv(data)


####### Parsing sm content ##################
with open('item_urls.csv', encoding='utf-8') as data_file:
    data = csv.reader(data_file)
    with ThreadPoolExecutor(max_workers=3) as executor:
        t1 = [executor.submit(get_item_content, row[1], row[0]) for row in data]


######## Parsing item urls ##################
# with open("catalog.txt", encoding='utf-8', mode='r') as file:
#     with ThreadPoolExecutor(max_workers=15) as executor:
#        t1 = [executor.submit(get_url_items, url.split(",")[1].strip(), url.split(',')[0]) for url in file]


# with open("catalog.txt", encoding='utf-8', mode='r') as file:
#     for line in file:
#         url = line.split(',')[1]
#         get_url_items(url)


# get_url_items("https://www.sulpak.kz/f/smartfoniy/almaty/1056_62")

# get_page_number('https://www.sulpak.kz/f/smartfoniy/almaty/1056_62')




