from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from os import getenv

app = Flask(__name__)

GEOLOCATION_API_URL = getenv('GEOLOCATION_API_URL')
WEATHER_API_URL = getenv('WEATHER_API_URL')
WEATHER_API_KEY = getenv('WEATHER_API_KEY')

load_dotenv()


def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip


@app.route('/api/hello', methods=['GET'])
def get_location():

    client_ip = get_client_ip()
    # Use geolocation service to get location data
    response = requests.get(GEOLOCATION_API_URL + client_ip)
    geo_data = response.json()

    # Extract relevant data
    city = geo_data.get('city', 'Unknown')
    visitor_name = request.args.get('visitor_name', '<No Name>')

    # get coordinates for weather retrieval
    city = geo_data.get('city', 'Unknown')
    lat = geo_data.get('lat')
    lon = geo_data.get('lon')

    # Use weather service to get weather data
    if lat and lon:
        weather_response = requests.get(WEATHER_API_URL, params={
            'lat': lat,
            'lon': lon,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        })
        weather_data = weather_response.json()
        temperature = weather_data.get('main', {}).get('temp', 'N/A')
    else:
        temperature = 'N/A'

    # Generate greeting message
    greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celcius in {city}"

    # Prepare response
    response_data = {
        "client_ip": client_ip,
        "location": city,
        "greeting": greeting
    }

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True)
