import string
from datetime import date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id_task = db.Column(db.Integer, primary_key = True)
    tanggal = db.Column(db.Date, default=date.today)
    kode = db.Column(db.String(10))
    jenis = db.Column(db.String(10))
    topik = db.Column(db.String(100))

class Keyword(db.Model):
    id_keyword = db.Column(db.Integer, primary_key = True)
    jenis = db.Column(db.String(10))


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == "__main__":
    app.run(debug=True,threaded=True)