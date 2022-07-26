# Instructions for the Amazon Microservice

The communication with the microservice will be performed using RabbitMQ, so the first thing will be to install it, you can follow the instructions on its webiste: [RabbitMQ Download](https://www.rabbitmq.com/download.html)

After that you need to open a conection and send the word/phrase of the product you need to look for on Amazon. It's important to use the queue  and routign key "keyword" for this purpose.

Here is an example sending the phrase "apple watch" on Python3:

```
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='keyword')
channel.basic_publish(exchange='',
                      routing_key='keyword',
                      body='apple watch')
```
                      
For the response you need to use the queue  and routign key "response". Here is an example of how we would receive a response on Python3:

```
channel = connection.channel()

channel.queue_declare(queue='response')

def callback(ch, method, properties, body):
    response_json = json.loads(body)
    print(" [x] Received %r" % response_json)

channel.basic_consume(queue='response', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
```

For more information on how to use RabbitMQ on other languages, please visit [RabbitMQ Get Started](https://www.rabbitmq.com/getstarted.html)
