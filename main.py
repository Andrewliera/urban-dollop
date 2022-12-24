from flask import Flask, render_template, request

app = Flask(__name__)


class BadInput(Exception):
    print("Bad input in form")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/zip_search', methods=['POST', 'GET'])
def zip_search():
    zip_input = ""
    try:
        if request.method == 'GET':
            return 'use form for submission'

        if request.method == 'POST':
            zip_input = request.form['searchZipCode']

    except TypeError:
        raise BadInput()

    return render_template('weather.html')


@app.route('/view_weather')
def view_weather():
    return render_template('weather.html')


if __name__ == '__main__':
    app.run(debug=True)
