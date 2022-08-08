from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import pika, sys, os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


NUMBER_OF_ITEMS = 10


# The following code is based on tutorial:
# https://medium.com/@jb.ranchana/web-scraping-with-selenium-in-python-amazon-search-result-part-1-f09c88090932
def get_amazon_results(keyword):
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    # create a driver object using driver_path as a parameter
    driver = webdriver.Chrome(options = options, service = Service(ChromeDriverManager().install()))
    # website to scrape
    web = 'https://www.amazon.com'
    driver.get(web)
    driver.get_screenshot_as_file("screenshotRODO.png")

    search_button = None
    search_box = None
    try:
        search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
    except:
        print("authenticated version of Amazon page")
    try:
        search_box = driver.find_element(By.ID, 'nav-bb-search')
    except:
        print("guest version of Amazon page")
    # type the keyword in search box
    search_box.send_keys(keyword)
    # create WebElement for a search button
    try:
        search_button = driver.find_element(By.ID, 'nav-search-submit-button')
    except:
        print("authenticated version of Amazon page")
    try:
        search_button = driver.find_element(By.ID, 'nav-bb-button')
    except:
        print("guest version of Amazon page")
    # click search_button
    search_button.click()
    # wait for the page to download
    driver.implicitly_wait(5)

    product_name = []
    product_asin = []
    product_price = []
    product_ratings = []

    items = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
    for i in range(0, NUMBER_OF_ITEMS):
        item = items[i]
        name = None
        try:
            name = item.find_element(By.XPATH, './/span[@class="a-size-medium a-color-base a-text-normal"]')
        except:
            print("article is of small vertical type")
        try:
            name = item.find_element(By.XPATH, './/span[@class="a-size-base-plus a-color-base a-text-normal"]')
        except:
            print("article is of big horizontal type")
        product_name.append(name.text)
        data_asin = item.get_attribute("data-asin")
        product_asin.append(data_asin)

        # find price
        whole_price = item.find_elements(By.XPATH, './/span[@class="a-price-whole"]')
        fraction_price = item.find_elements(By.XPATH, './/span[@class="a-price-fraction"]')

        if whole_price != [] and fraction_price != []:
            price = '.'.join([whole_price[0].text, fraction_price[0].text])
        else:
            price = 0
        product_price.append(price)

        # find ratings
        ratings_box = item.find_elements(By.XPATH, './/div[@class="a-row a-size-small"]/span')
        if ratings_box != []:
            ratings = ratings_box[0].get_attribute('aria-label')
        else:
            ratings = 0

        product_ratings.append(ratings)

    driver.quit()
    dict = {}
    for i in range(0, len(product_name)):
        dict[i] = {"product_name" : product_name[i], "product_asin" : product_asin[i], "product_price" : product_price[i], "product_rating" : product_ratings[i]}
    jsonString = json.dumps(dict, indent=4)
    return jsonString


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='keyword')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        keyword = str(body.decode())
        response = get_amazon_results(keyword)
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='response')
        channel.basic_publish(exchange='',
                              routing_key='response',
                              body=response)
        print(" [x] Sent : '", response, "'")

    channel.basic_consume(queue='keyword', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
