from flask import Flask


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('paano.config')
app.config.from_pyfile('application.cfg', silent=True)
application = app
