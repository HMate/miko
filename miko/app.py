import os

import flask
import flask_sqlalchemy
import sqlalchemy.exc
import utils
import pika


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MIKO_DB_CONNSTRING"]
app.json_encoder = utils.MikoJsonEncoder
db = flask_sqlalchemy.SQLAlchemy(app)


@app.route('/test')
@app.route('/test/<int:num>')
def test(num):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='miko_mq'))
    channel = connection.channel()

    channel.queue_declare(queue='miko_msg')

    channel.basic_publish(exchange='', routing_key='miko_msg', body='Hello Miko Database %s!'%num)
    print(" [x] Sent 'Hello Miko %s!'" % num)
    connection.close()
    return "OK"


@app.route('/book')
@app.route('/book/<int:uid>')
def books(uid=-1):
    if uid >= 0:
        res = db.engine.execute("select * from books where uid = %(uid)s", uid=uid)
        rows = [dict(row) for row in res]
    else:
        res = db.engine.execute("select * from books")
        rows = [dict(row) for row in res]
    return flask.jsonify(rows)


@app.route('/book/insert', methods=["POST"])
def book_insert():
    data = flask.request.json
    print(data)

    try:
        db.engine.execute("INSERT INTO books(title, publisher, publish_year, author, acquire_date, issue_count) VALUES" +
                          "(%(title)s, %(publisher)s, %(publish_year)s, %(author)s, %(acquire_date)s, %(issue_count)s)",
                          **data)
    except (sqlalchemy.exc.DataError) as e:
        print("ERROR in book_insert: {}".format(e))
        return "Failed because: {}".format(e.orig)
    except KeyError as e:
        print("ERROR in book_insert: {}".format(e))
        return "Failed because missing property {}".format(e)
    return "New books inserted"


@app.route('/stat/<string:stat_name>')
def stat(stat_name):
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
    if stat_name in allowed_stats:
        # We whitelist table names to protect against sql injection
        query = "select * from " + stat_name
        res = db.engine.execute(query)
        rows = [dict(row) for row in res]
    return flask.jsonify(rows)


if __name__ == '__main__':
    # for development on local machine
    app.run(debug=True, port=5000)