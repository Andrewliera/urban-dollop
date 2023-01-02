from flask import Flask, render_template, request
import requests
from enum import Enum
import configparser


app = Flask(__name__)


class KeyConfigError(Exception):
    print("Error Configuring key")


class BadInput(Exception):
    print("Bad input in form")


class BadKey(Exception):
    print("Problem With API key used")


class BadWeatherInput(Exception):
    print("Bad input in getting Weather")


class GetConditionsError(Exception):
    print("Problem with Getting Conditions")


class GetForecastError(Exception):
    print("Problem with Getting Forecast")


class UrlCalls(Enum):
    LOCATION = 1
    CONDITION = 2
    FORECAST = 3


class TempKey:
    try:
        config = configparser.ConfigParser()
        config.read('app.config')
        config.sections()
        curr_key = config['secrets']['apikey']
    except KeyConfigError:
        raise KeyConfigError()


def url_factory(call_type,api_key, additional_data):
    try:
        if call_type == UrlCalls.LOCATION:
            return 'http://dataservice.accuweather.com/locations/v1/postalcodes/search?apikey={}' \
                   '&q={}'.format(api_key, additional_data)
        elif call_type == UrlCalls.CONDITION:
            return 'http://dataservice.accuweather.com/currentconditions/v1/' \
                   '{}?apikey={}'.format(additional_data, api_key)
        elif call_type == UrlCalls.FORECAST:
            return 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/' \
                   '{}?apikey={}'.format(additional_data, api_key)
    except BadKey:
        raise BadKey()


def get_location(user_zip):
    location = url_factory(UrlCalls.LOCATION, TempKey.curr_key, user_zip)
    response = requests.get(location)
    json_version_key = response.json()[0].get('Key')
    json_version_name = response.json()[0].get('EnglishName')
    try:
        temp_dict = {'key': json_version_key, 'location': json_version_name}
    except RuntimeError:
        return RuntimeError
    return temp_dict


def get_condition(key):
    curr_conditions = url_factory(UrlCalls.CONDITION, TempKey.curr_key, key)
    response = requests.get(curr_conditions)
    json_version = response.json()
    json_version_conditions = json_version[0].get('WeatherText')
    json_version_celsius = json_version[0]['Temperature']['Metric']['Value']
    json_version_fahrenheit = json_version[0]['Temperature']['Imperial']['Value']
    try:
        print("The current forecast is {}".format(json_version[0].get('WeatherText')))
        temp_dict = {
                'conditions': json_version_conditions,
                'conditions_celsius': json_version_celsius,
                'conditions_fahrenheit': json_version_fahrenheit
                     }

    except GetConditionsError:
        raise GetConditionsError()
    return temp_dict


#def get_forecast(key):
#    forcast = url_factory(UrlCalls.FORECAST, TempKey.curr_key, key)
#    response = requests.get(forcast)
#    json_version = response.json()

#    try:
#        for i in range(0, 4):
#            print(json_version['DailyForecasts'][i]['Date'] + " will be: "
#                  + json_version['DailyForecasts'][i]['Day']['IconPhrase'])
#        foo = json_version['DailyForecasts'][0]['Day']['IconPhrase']
#    except GetForecastError:
#        raise GetForecastError()
#    return foo

def weather_check(user_in):
    try:
        locate = get_location(user_in)

        location_key = locate.get('key')
        curr_location = locate.get('location')

        my_dict = {
                'curr_location': curr_location,
                'curr_conditions': get_condition(location_key)
                }
    except BadWeatherInput:
        raise BadWeatherInput()
    return my_dict

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/zip_search', methods=['POST', 'GET'])
def zip_search():
    try:
        if request.method == 'GET':
            return 'use form for submission'

        if request.method == 'POST':
            zip_input = request.form['searchZipCode']
            weather_response = weather_check(zip_input)

            response_location = weather_response.get('curr_location')
            response_condition = weather_response['curr_conditions'].get('conditions')
            response_degrees = weather_response['curr_conditions'].get('conditions_fahrenheit')

            temp_dict = {
                'location' : response_location,
                'condition' : response_condition,
                'degrees' : response_degrees
            }

            print(weather_response)

    except TypeError:
        raise BadInput()

    return render_template('weather.html', my_dict = temp_dict)

if __name__ == '__main__':
    app.run(debug=True)
