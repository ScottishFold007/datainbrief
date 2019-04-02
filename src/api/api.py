from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/price')
def generate_price():

    return price


if __name__ == '__main__':
    app.run(debug=True)