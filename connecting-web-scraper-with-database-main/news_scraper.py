import os
PYPPETEER_CHROMIUM_REVISION = '1263111'
os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION

import time
import datetime
from requests_html import HTMLSession
from mysql.connector import Error
from data_connection import create_data_connection
from insert_news import (
    execute_query,
    insert_reporter,
    get_reporter_id,
    insert_category,
    get_category_id,
    insert_news,
    get_news_id,
    insert_publisher,
    get_publisher_id,
    insert_image
)

def process_and_insert_news_data(connection, publisher_website, publisher, title, reporter, news_datetime, category, images, url):
    try:
        category_id = insert_category(connection, category, f"{category} সম্পর্কিত")
        c_id = get_category_id(connection, category)
        
        reporter_id = insert_reporter(connection, reporter, f"{reporter}@gmail.com")
        r_id = get_reporter_id(connection, reporter)
        
        publisher_id = insert_publisher(connection, publisher, f"{publisher_website}")
        p_id = get_publisher_id(connection, publisher)
        
        news_id = insert_news(connection, c_id, r_id, p_id, news_datetime, title, news_body, url)
        n_id = get_news_id(connection, title)
        
        for image_url in images:
            image_id = insert_image(connection, n_id, image_url)
    except Error as e:
        print(f"Error while processing news data - {e}")

def single_news_scraper(url):
    session = HTMLSession()
    try:
        response = session.get(url)
        response.html.render()
        time.sleep(3)

        publisher_website = url.split('/')[2]
        publisher = publisher_website.split('.')[-2]

        title = response.html.find('h1', first=True).text
        reporter = response.html.find('.contributor-name', first=True).text
        
        datetime_element = response.html.find('time', first=True)
        news_datetime = datetime_element.attrs['datetime']
        category = response.html.find('.print-entity-section-wrapper', first=True).text

        news_body = '\n'.join([p.text for p in response.html.find('p')])

        img_tags = response.html.find('img')
        images = [img.attrs['src'] for img in img_tags if 'src' in img.attrs]
        
        return publisher_website, publisher, title, reporter, news_datetime, category, news_body, images
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    conn = create_data_connection()
    if conn is not None:
        url = "https://www.prothomalo.com/lifestyle/fashion/zs78004xl0"
        publisher_website, publisher, title, reporter, news_datetime, category, news_body, images = single_news_scraper(url)
        process_and_insert_news_data(conn, publisher_website, publisher, title, reporter, news_datetime, category, images, url)