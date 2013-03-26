from paano import app, extensions


if __name__ == '__main__':
    extensions.init(app)
    app.run(debug=True)
