import csv
import sys
import os
import time
import openpyxl
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver.v2 as uc
from methods import create_csv, get_product_urls, get_product, scrape_products

start = time.time()
url_ = 'https://www.barcodelookup.com/'

# check if brands.xlsx exists
if not os.path.exists('brands.xlsx'):
    print('brands.xlsx is not present in the directory')
    time.sleep(4)
    sys.exit()

# create csv
filename = create_csv()
wb = openpyxl.load_workbook("brands.xlsx")
ws = wb.active

try:
    for cell in ws['A']:
        keyword = str(cell.value)
        keyword = keyword.replace(',', '').replace('"', '').replace("'", '').replace('!', '')
        print(f"\n\nSearching Keyword \'{keyword}\'")
        keyword = '-'.join(keyword.split())
        # ===================== Search Keywords =====================
        options = uc.ChromeOptions()
        options.headless = True
        driver = uc.Chrome(options=options)
        # driver = uc.Chrome()
        main_url = url_ + keyword
        driver.get(main_url)
        time.sleep(3)
        body = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        ).get_attribute('outerHTML')
        soup = BeautifulSoup(body, "lxml")

        # There are 3 Cases when url is visited
        # (1) Directly land to product page (https://www.barcodelookup.com/3663535097234)
        # (2) Land to list of products (https://www.barcodelookup.com/candy)
        # (3) No results found (https://www.barcodelookup.com/Night_man)

        # =====================  Checking Case 1 =====================
        product_details = get_product(soup)
        if product_details:
            print("1 Product found...")
            print("Scraping the Product details...")
            with open(filename, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(product_details)
                f.close()
        # ===================== Checking Case 2 =====================
        elif soup.find_all('ul', {'id': 'product-search-results'}):
            product_urls = get_product_urls(driver, soup)
            scrape_products(filename, product_urls)

        # ===================== Case 3 =====================
        else:
            print("No results found for this keyword")
            time.sleep(3)
            sys.exit()

    end = time.time()
    print("\nCompleted in", int((end - start) / 60), "minutes")
    print(f"Please see the {filename} file")
    time.sleep(3)
    sys.exit()
except Exception as error:
    print('Error: ', error)
    time.sleep(10)
