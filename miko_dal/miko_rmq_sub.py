"""
This application is responsible for listening for messages on ampq exchanges,
and communicating with the miko postgres database.

author: Hidvégi Máté
"""
import json
import os
import time

import pika
import pika.exceptions
import sqlalchemy
import sqlalchemy.exc


def on_msg(ch, method, props, body):
    print("Got %s" % body, flush=True)


def insert_book(ch, method, props, body):
    data = json.loads(body)
    try:
        engine.execute("INSERT INTO books(title, publisher, publish_year, author, acquire_date, issue_count) VALUES" +
                          "(%(title)s, %(publisher)s, %(publish_year)s, %(author)s, %(acquire_date)s, %(issue_count)s)",
                          **data)
    except sqlalchemy.exc.DataError as e:
        print("ERROR in book_insert: {}".format(e))
        return "Failed because: {}".format(e.orig)
    except KeyError as e:
        print("ERROR in book_insert: {}".format(e))
        return "Failed because missing property {}".format(e)
    return "New books inserted"


def start_rabbit_listener():
    print('Connecting to rabbitmq...')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="miko_mq"))
    channel: pika.adapters.blocking_connection.BlockingChannel = connection.channel()

    queue_map = {"miko_msg": on_msg}
    for queue, handler in queue_map.items():
        channel.queue_declare(queue=queue)
        channel.basic_consume(queue=queue, on_message_callback=handler, auto_ack=True)

    print('Waiting for messages from miko. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    engine: sqlalchemy.engine.Engine = sqlalchemy.create_engine(os.environ["MIKO_DB_CONNSTRING"])

    # When rabbitmq container is started, it initializes slower then this container.
    # We try to connect a couple times, but give up if its not up even after that.
    retries = 5
    while retries > 0:
        try:
            start_rabbit_listener()
            retries = 0
        except pika.exceptions.AMQPConnectionError:
            time.sleep(3)
            retries -= 1
