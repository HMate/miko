"""
This application is a REST api for miko service.
It accepts web api reqests and places corresponding requests into rabbitmq for the database.

author: Hidvégi Máté
"""
import json
import os

import flask
from flask import request
import utils


app = flask.Flask(__name__)
mq = utils.MQClient(os.environ["MIKO_MQ_HOST"])


@app.route('/books')
def books():
    args = request.args
    results = mq.send_wait_response("miko.book.query", json.dumps(args))
    results = json.loads(results)
    return flask.jsonify(results)


@app.route('/books/insert', methods=["POST"])
def book_insert():
    data = flask.request.json
    data_json = json.dumps(data)
    results = mq.send_wait_response("miko.book.insert", data_json)
    return results


@app.route('/stat/<string:stat_name>')
def stat(stat_name):
    results = mq.send_wait_response("miko.stat", stat_name)
    results = json.loads(results)
    return flask.jsonify(results)


if __name__ == '__main__':
    # for development on local machine
    app.run(debug=True, port=5000)