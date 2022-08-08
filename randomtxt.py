from bs4 import BeautifulSoup
import requests
import random
import pika


# text generation function
# Based on these two tutorials:
# 1) https://www.geeksforgeeks.org/web-scraping-from-wikipedia-using-python-a-complete-guide/
# 2) https://www.freecodecamp.org/news/scraping-wikipedia-articles-with-python/
def text_generation(link):
    # open a webpage with http requests
    print(f"[randomtxt] Pulling text from {link}")
    response = requests.get(
    	url="https://en.wikipedia.org" + link,
    )
    # parse it with beautiful soup so that we can pull a paragraph from it
    wiki_soup = BeautifulSoup(response.content, 'html.parser')

    # set our randomly generated text variable with beautiful soup commands
    return wiki_soup.find_all('p')[0].get_text()


# Setup communication channel
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='text_gen')


# What to do when we receive a request:
def on_request(chann, method, props, body):
    print(" [randomtxt.py] generating text....")
    # Generate the text
    possibleLinks = ["/wiki/Link_farm", "/wiki/Belgian_National_Day", "/wiki/Biological_specimen",
        "/wiki/Standard_operating_procedure", "/wiki/Checklist", "/wiki/Software_engineering",
        "/wiki/Decision-making", "/wiki/Mental_model", "/wiki/User_interface_design"]
    random.shuffle(possibleLinks)
    message = text_generation(possibleLinks[0])
    print(f" [randomtxt] sending message: {message}")
    # And then send it back
    chann.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(message))
    chann.basic_ack(delivery_tag=method.delivery_tag)

# Actually receive requests and send responses
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='text_gen', on_message_callback=on_request)

print(" [randomtxt.py] Waiting for random text generation requests")
channel.start_consuming()