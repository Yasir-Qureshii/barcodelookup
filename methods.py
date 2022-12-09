import csv
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver.v2 as uc


def generate_filename(csv_file=False):
    """ docstring """
    ext = '.xlsx'
    if csv_file:
        ext = '.csv'
    now = datetime.now()
    xx = 'Output_' + str(now)[:-7] + ext
    xx = xx.replace(' ', '_').replace(':', '-')
    return xx


def create_csv():
    filename = 'Output.csv'
    if os.path.exists(filename):
        filename = generate_filename(csv_file=True)

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Barcode Formats', 'Category', 'Manufacturer', 'Brand'])
        f.close()

    return filename


def get_product(soup_product_page):
    """ docstring """
    barcode = category = manufacturer = brand = None
    try:
        card = soup_product_page.find('div', class_='product-details')
        name = card.find('h4').text.strip()
        name = name.replace('"', '').replace("'", '')
        labels = card.find_all('div', 'product-text-label')
        for label in labels:
            if 'Barcode Formats:' in label.text:
                barcode = label.text.replace('Barcode Formats:', '').strip()
            elif 'Category:' in label.text:
                category = label.text.replace('Category:', '').strip()
            elif 'Manufacturer:' in label.text:
                manufacturer = label.text.replace('Manufacturer:', '')
            elif 'Brand:' in label.text:
                brand = label.text.replace('Brand:', '').strip()

        return [name, barcode, category, manufacturer, brand]
    except Exception as error:
        # print('error in get_product: ', error)
        return None


def get_product_urls(driver, soup_list_page):
    """ docstring """
    output = []
    a_tags = soup_list_page.find('ul', {'id': 'product-search-results'}).find_all('a')
    for a in a_tags:
        output.append(a['href'])

    # Check if next exists
    has_next = False
    next_page = soup_list_page.find('ul', 'pagination').find('li', 'active').find_next_sibling()
    if next_page:
        has_next = True

    base_url = driver.current_url
    if base_url.endswith('/'):
        base_url = base_url[:-1]

    # if next page exists
    current_page = 1
    while has_next:
        next_page = current_page + 1
        page_url = base_url + f'/{next_page}'
        try:
            driver.get(page_url)
            body = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            ).get_attribute('outerHTML')
            # body = driver.find_element(By.TAG_NAME, 'body')
            soup_list_page = BeautifulSoup(body, "lxml")
            a_tags = soup_list_page.find('ul', {'id': 'product-search-results'}).find_all('a')
            for a in a_tags:
                output.append(a['href'])
                print(f'Found {len(output)} Products ...', end='\r')

            # Check if next exists
            pagination = soup_list_page.find_all('ul', 'pagination')
            if pagination:
                next_page_exists = pagination[0].find('li', 'active').find_next_sibling()
                if next_page_exists:
                    has_next = True
                    current_page = next_page
                else:
                    has_next = False
            else:
                has_next = False
        except:
            pass
    driver.close()
    return output


def scrape_products(filename, urls):
    print(f"{len(urls)} Total Products Found...")
    print("Scraping the Product details...")
    results = []
    queue = []
    options = uc.ChromeOptions()
    options.headless = True
    driver = uc.Chrome(options=options)
    # driver = uc.Chrome()
    products_scraped = 0
    # with open(filename, 'a', encoding='utf-8', newline='') as f:
    #     writer = csv.writer(f)
    for url in urls:
        try:
            driver.get(url)
            body = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            ).get_attribute('outerHTML')
            soup = BeautifulSoup(body, "lxml")
            row = get_product(soup)
            if row:
                # writer.writerow(row)
                results.append(row)
                products_scraped += 1
                print(f'{products_scraped} Products Scraped...', end='\r')
            else:
                queue.append(url)
        except Exception as error:
            print("error in scrape_products: ", error)
            queue.append(url)
    driver.close()
        # f.close()

    # with open(filename, 'a', encoding='utf-8', newline='') as f:
    #     writer = csv.writer(f)
    while len(queue) > 0:
        options = uc.ChromeOptions()
        options.headless = True
        driver = uc.Chrome(options=options)
        # driver = uc.Chrome()
        for index, url in enumerate(queue):
            try:
                driver.get(url)
                body = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                ).get_attribute('outerHTML')
                soup = BeautifulSoup(body, "lxml")
                row = get_product(soup)
                if row:
                    # writer.writerow(row)
                    results.append(row)
                    del queue[index]
                    products_scraped += 1
                    print(f'{products_scraped} Products Scraped...', end='\r')
            except Exception as error:
                pass
        driver.close()
        # f.close()

    print(f'{len(results)} Total Products Scraped')
    with open(filename, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)
        f.close()



