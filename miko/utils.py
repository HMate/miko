import uuid
import typing

import pika


def send_one_way(queue, message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='miko_mq'))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    channel.basic_publish(exchange='', routing_key=queue, body=message)
    connection.close()


class ResponseWrapper(object):
    def __init__(self, response_handler, corr_id):
        self.corr_id = corr_id
        self.response = None
        self.response_handler = response_handler
        self.done = False

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = self.response_handler(body)
            self.done = True


def send_wait_response(queue: str, message: str, response_handler: typing.Callable[[str], typing.Any]):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='miko_mq'))
    channel: pika.adapters.blocking_connection.BlockingChannel = connection.channel()

    response = channel.queue_declare(queue="", exclusive=True)
    response_queue = response.method.queue
    corr_id = str(uuid.uuid4())
    wrapper = ResponseWrapper(response_handler, corr_id)

    channel.basic_consume(queue=response_queue,
                          on_message_callback=wrapper.on_response,
                          auto_ack=True)

    channel.basic_publish(exchange='', routing_key=queue,
                          properties=pika.BasicProperties(
                              reply_to=response_queue,
                              correlation_id=corr_id),
                          body=message)
    while wrapper.done is False:
        connection.process_data_events()
    connection.close()
    return wrapper.response