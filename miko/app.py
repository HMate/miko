"""
This application is a REST api for miko service.
It accepts web api reqests and places corresponding requests into rabbitmq for the database.

author: Hidvégi Máté
"""
import json
import flask
import utils


app = flask.Flask(__name__)


@app.route('/books')
@app.route('/books/<int:uid>')
def books(uid=-1):
    def process_response(body):
        return json.loads(body)

    results = utils.send_wait_response("miko.book.query", str(uid), process_response)
    return flask.jsonify(results)


@app.route('/books/insert', methods=["POST"])
def book_insert():
    def process_response(body):
        return body

    data = flask.request.json
    data_json = json.dumps(data)
    results = utils.send_wait_response("miko.book.insert", data_json, process_response)
    return results


@app.route('/stat/<string:stat_name>')
def stat(stat_name):
    def process_response(body):
        return json.loads(body)

    results = utils.send_wait_response("miko.stat", stat_name, process_response)
    return flask.jsonify(results)


if __name__ == '__main__':
    # for development on local machine
    app.run(debug=True, port=5000)