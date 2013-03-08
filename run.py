from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config.py')

db = SQLAlchemy(app)
db.init_app(app)

@app.before_request
def before_request():
    g.db = db

if __name__ == '__main__':
    app.run()


