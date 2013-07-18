from flask import Flask


app = Flask(__name__, static_url_path='/paano/static',
            instance_relative_config=True)
app.config.from_object('paano.config')
app.config.from_pyfile('application.cfg', silent=True)
application = app
