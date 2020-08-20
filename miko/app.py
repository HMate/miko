import os

import flask
import flask_sqlalchemy
import utils


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MIKO_DB_CONNSTRING"]
app.json_encoder = utils.MikoJsonEncoder
db = flask_sqlalchemy.SQLAlchemy(app)


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