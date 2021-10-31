from flask.json import jsonify
import requests
from requests.exceptions import HTTPError

url = '0.0.0.0:8080/hello'

class Detector:
    def __init__(self, name) -> None:
        registration = jsonify({
            'name': name,
            'role': self.__class__
        })
        
        try:
            response = requests.post(url = url, data = registration)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('Success!')
