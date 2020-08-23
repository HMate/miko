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

import utils


def query_books(ch, method, props, body):
    print("Incoming query_books message {}".format(body), flush=True)
    try:
        data = json.loads(body)
        where = utils.to_sql_where_constraint(
            data, like_columns=["author", "publisher", "title", "acquire_date"])
        query = "select * from books{}".format(where)
        print("Running query: {}".format(query))
        res = engine.execute(query, **data)
        rows = [dict(row) for row in res]
    except Exception as e:
        print("Got error in query_books: {}".format(e))
        rows = []

    result = json.dumps(rows, cls=utils.MikoJsonEncoder)

    send_rpc_result(ch, method, props, result)


def insert_book(ch, method, props, body):
    print("Incoming insert_book message {}".format(body), flush=True)
    data = json.loads(body)
    result = "New books inserted"
    try:
        engine.execute("INSERT INTO books(title, publisher, publish_year, author, acquire_date, issue_count) VALUES" +
                          "(%(title)s, %(publisher)s, %(publish_year)s, %(author)s, %(acquire_date)s, %(issue_count)s)",
                          **data)
    except sqlalchemy.exc.DataError as e:
        print("ERROR in book_insert: {}".format(e))
        result = "Failed because: {}".format(e.orig)
    except KeyError as e:
        print("ERROR in book_insert: {}".format(e))
        result = "Failed because missing property {}".format(e)

    send_rpc_result(ch, method, props, result)


def stat(ch, method, props, body:bytes):
    print("Incoming stat message {}".format(body), flush=True)
    allowed_stats = [
        "average_books_age",
        "author_book_count",
        "publisher_book_count",
        "oldest_youngest_books",
        "author_books_until_year",
        "author_average_acquire",
        "author_third_book_issues"
    ]
    rows = []
    stat_name = body.decode("UTF8")
    if stat_name in allowed_stats:
        # We whitelist table names to protect against sql injection
        query = "select * from " + stat_name
        res = engine.execute(query)
        rows = [dict(row) for row in res]
    result = json.dumps(rows, cls=utils.MikoJsonEncoder)
    send_rpc_result(ch, method, props, result)


def send_rpc_result(ch, method, props, result):
    print("Sending result {}".format(result), flush=True)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(result))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_rabbit_listener():
    print('Connecting to rabbitmq...')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="miko_mq"))
    channel: pika.adapters.blocking_connection.BlockingChannel = connection.channel()

    rpc_queue_map = {
        "miko.book.query": query_books,
        "miko.book.insert": insert_book,
        "miko.stat": stat
    }
    for queue, handler in rpc_queue_map.items():
        channel.queue_declare(queue=queue)
        channel.basic_consume(queue=queue, on_message_callback=handler)

    channel.basic_qos(prefetch_count=1)
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
