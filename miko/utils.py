import uuid

import pika
from pika.adapters.blocking_connection import BlockingChannel


class MQClient(object):
    def __init__(self, host):
        self.host = host

    def send_one_way(self, queue: str, message: str):
        """Sends a message to the given rmq queue without waiting for response."""
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host))
        channel: BlockingChannel = connection.channel()

        channel.queue_declare(queue=queue)

        channel.basic_publish(exchange='', routing_key=queue, body=message)
        connection.close()

    def send_wait_response(self, queue: str, message: str):
        """Sends a message to the given rmq queue and waits for response.
        """
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host))
        channel: BlockingChannel = connection.channel()

        response = channel.queue_declare(queue="", exclusive=True)
        response_queue = response.method.queue
        corr_id = str(uuid.uuid4())
        wrapper = ResponseWrapper(corr_id)

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


class ResponseWrapper(object):
    """
    This class is used for handling and storing the response messages of rabbitmq rpc calls.
    It's needed because python local functions cannot be used as closures, 
    so its hard to modify the values of the enclosing function.
    """
    def __init__(self, corr_id):
        self.corr_id = corr_id
        self.response = None
        self.done = False

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
            self.done = True
