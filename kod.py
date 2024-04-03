import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers_param = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15"
}


def scrape_page(newUrl):
    location = author = content = "NOT DEFINED"
    try:

        if newUrl[0] == "/":
            newUrl = "https://www.eeas.europa.eu" + newUrl

        if newUrl.startswith("https://ec.europa.eu/commission/"):
            driver = webdriver.Chrome()
            try:
                driver.get(newUrl)
                title_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.ecl-page-header__title'))
                )

                title = title_element.text.strip()
                content_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.ecl-paragraph-detail'))
                )

                content = content_element.text.strip()
                location_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "(//span[@class='ecl-page-header__meta-item'])[last()]"))
                )

                location = location_element.text.strip()

            except Exception as e:
                print(f"An error occurred: {e}")

            finally:
                driver.quit()

        else:
            location = "NOT SUPPORTED FOR NOW"
            author = "NOT SUPPORTED FOR NOW"
            content = "NOT SUPPORTED FOR NOW"
        print("last one: ", title)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making a request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return location, author, content


def next_page_exists(url):
    pressMaterialPage = requests.get(url, headers=headers_param)
    news = pressMaterialPage.content
    soup = BeautifulSoup(news, "html.parser")
    next_page_button = soup.find('a', {'title': 'Go to next page'})
    if next_page_button:
        print("True condition", next_page_button)
        return True
    else:
        print("False condition", next_page_button)
        return False


import pandas as pd


def content_topic():
    existing_data = pd.read_excel('/Users/denizterziler/Desktop/ec_europa_eu_20.xlsx') #okunması gereken büyük dosya

    unique_urls = existing_data['URL'].unique()

    scraped_data_list = []

    for url in unique_urls:
        loc, aut, cont = scrape_page(url)
        scraped_data_list.append({
            'URL': url,
            'Location': loc,
            'Author': aut,
            'Content': cont
        })

    scraped_data_df = pd.DataFrame(scraped_data_list)

    merged_data = pd.merge(existing_data, scraped_data_df, on='URL', how='left')

    merged_data = merged_data.loc[:, ~merged_data.columns.duplicated()]

    final_columns = ['', 'Subtitle', 'Title', 'Date', 'URL', 'Location_Tag', 'Topic_Tag', 'Location', 'Author',
                     'Content']

    merged_data.columns = final_columns
    #nereye save edilmesi gerekiyorsa o dosya adı.
    merged_data.to_excel('/Users/denizterziler/PycharmProjects/pythonWebScrapingProject/eees__deneme.xlsx', index=False)


if __name__ == '__main__':
    content_topic()
