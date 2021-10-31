from flask.json import jsonify
import requests
from requests import exceptions
from requests.exceptions import HTTPError

url = "http://0.0.0.0:8080/hello"


class Tunneler:
    def __init__(self, name) -> None:
        role = self.__class__
        registration = jsonify(
            {   "role": role,
                "name": name
            }
        )
        try:
            response = requests.post(url=url, data = registration)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print("Success! The data returned from the server is:", str(response))

if __name__ == '__main__':
    tunneler = Tunneler("PythonClient")