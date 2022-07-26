import pika, sys, os

RESPONSE = "muchos wireless chargers bien baratos"


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='keyword')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='response')
        channel.basic_publish(exchange='',
                              routing_key='response',
                              body=RESPONSE)
        print(" [x] Sent : '", RESPONSE, "'")

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