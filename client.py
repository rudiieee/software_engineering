import pika, sys, os, json


def main():
    KEYWORD = "wireless charger"
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='keyword')
    channel.basic_publish(exchange='',
                          routing_key='keyword',
                          body=KEYWORD)
    print(" [x] Sent : '", KEYWORD, "'")
    # connection.close()
    channel = connection.channel()

    channel.queue_declare(queue='response')

    def callback(ch, method, properties, body):
        response_json = json.loads(body)
        print(" [x] Received %r" % response_json)

    channel.basic_consume(queue='response', on_message_callback=callback, auto_ack=True)

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