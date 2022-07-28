from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import pika, sys, os

def get_amazon_results(keyword):
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # create a driver object using driver_path as a parameter
    driver = webdriver.Chrome(options = options, service = Service(ChromeDriverManager().install()))
    # assign your website to scrape
    web = 'https://www.amazon.com'
    driver.get(web)

    # import more
    from selenium.webdriver.common.by import By
    # assign any keyword for searching
    # keyword = "wireless charger"
    # create WebElement for a search box
    search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
    # type the keyword in searchbox
    search_box.send_keys(keyword)
    # create WebElement for a search button
    search_button = driver.find_element(By.ID, 'nav-search-submit-button')
    # click search_button
    search_button.click()
    # wait for the page to download
    driver.implicitly_wait(5)
    # quit the driver after finishing scraping (please keep this line at the bottom)
    # driver.quit()


    product_name = []
    product_asin = []
    product_price = []
    product_ratings = []
    product_ratings_num = []
    product_link = []



    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    items = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
    for i in range(0, 2):
        item = items[i]
        name = None
        try:
            name = item.find_element(By.XPATH, './/span[@class="a-size-medium a-color-base a-text-normal"]')
        except:
            print("article is not of big horizontal type")
        try:
            name = item.find_element(By.XPATH, './/span[@class="a-size-base-plus a-color-base a-text-normal"]')
        except:
            print("article is not of small vertical type")
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

        # find ratings box
        ratings_box = item.find_elements(By.XPATH, './/div[@class="a-row a-size-small"]/span')

        # find ratings and ratings_num
        if ratings_box != []:
            ratings = ratings_box[0].get_attribute('aria-label')
            # ratings_num = ratings_box[1].get_attribute('aria-label')
        else:
            ratings = 0

        product_ratings.append(ratings)
        # product_ratings_num.append(str(ratings_num))

    # following print statement is for checking that we correctly scrape data we want
    driver.quit()
    dict = {}
    for i in range(0, len(product_name)):
        dict[i] = {"product_name" : product_name[i], "product_asin" : product_asin[i], "product_price" : product_price[i], "product_rating" : product_ratings[i]}
    # print(product_name)
    # print(product_asin)
    # print(product_price)
    # print(product_ratings)
    # print(dict)
    jsonString = json.dumps(dict, indent=4)
    # print(jsonString)
    return jsonString


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='keyword')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        keyword = str(body)
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
