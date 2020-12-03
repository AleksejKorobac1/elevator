import requests

url = 'http://127.0.0.1:8000/control'

myobj = {
    'request_from': 5,
    'request_to': 8
}

x = requests.post(url, data = myobj)

print(x.status_code, x.text)