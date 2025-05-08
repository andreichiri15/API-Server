import requests

url = 'http://localhost:5000/api/state_mean'
data = {
    "question": "Percent of adults who report consuming fruit less than one time daily",
    "state": "Wyoming"
}

x = requests.post(url, json=data)

print(x.text)

url = 'http://localhost:5000/api/state_mean'

data = {
    "question": "Percent of adults who report consuming fruit less than one time daily",
    "state": "Connecticut"
}

x = requests.post(url, json=data)

print(x.text)

url = 'http://localhost:5000/api/get_results/1'

x = requests.get(url)

print(x.text)

url = 'http://localhost:5000/api/get_results/2'

x = requests.get(url)

print(x.text)

url = 'http://localhost:5000/api/graceful_shutdown'

x = requests.get(url)

print(x.text)
