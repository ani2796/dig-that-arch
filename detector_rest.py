import requests
from flask import Flask
from requests.exceptions import HTTPError
from flask_socketio import SocketIO, send

flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(flask_app)

url = 'http://0.0.0.0:8080/'
reg = 'registration'

@socketio.on('message')
def handle_message(message):
    send(message)

class Detector:
    def __init__(self, name) -> None:
        role = self.__class__.__name__
        params = dict({
            'name': name,
            'role': role
        })
        try:
            reg_url = url + reg
            response = requests.get(url = reg_url, params = params)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('Success!' + str(response.content))

if __name__ == '__main__':
    detector = Detector("DetectorClient")

