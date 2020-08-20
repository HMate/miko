import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MIKO_DB_CONNSTRING"]
db = SQLAlchemy(app)


@app.route('/book')
@app.route('/book/<int:uid>')
def books(uid=-1):
    rows = []
    if uid >= 0:
        res = db.engine.execute("select * from books where uid = %(uid)s", uid=uid)
        rows = [dict(row) for row in res]
    else:
        res = db.engine.execute("select * from books")
        rows = [dict(row) for row in res]
    return jsonify(rows)


@app.route('/stat/author_third_book_issues')
def author_third_book_issues():
    res = db.engine.execute("select * from author_third_book_issues")
    rows = [dict(row) for row in res]
    return jsonify(rows)


if __name__ == '__main__':
    app.run(debug=True, port=5000)