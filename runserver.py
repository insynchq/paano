from paano import app, extensions, views


if __name__ == '__main__':
    extensions.init(app)
    views.init(app)
    app.run(debug=True)
