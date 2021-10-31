import requests
from requests.exceptions import HTTPError

url = 'http://0.0.0.0:8080/'
reg = 'registration'

class Tunneler:
    def __init__(self, name) -> None:
        params = dict({
            'name': name,
            'role': self.__class__.__name__
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
    detector = Tunneler("TunnelerClient")