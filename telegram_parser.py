import requests

def login(email , password):
    url = 'http://localhost/api/login/'
    data = {
        'email': email,
        'password': password
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        
        return response.json() 
    else:
        return None

def profiles():
    url = 'http://localhost/api/profiles/'

    response = requests.get(url)
    result = ''
    for prof in response.json():
        result = prof
    if response.status_code == 200:
        return result
    else:
        return 'Не найдено профилей'
print(profiles())  
def my_profile(bearer_token):
    url = 'http://localhost/api/profiles/my_profile/'
    data = {
        'token': f'Bearer {bearer_token}'
    }

    response = requests.get(url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# print(login('almashnurmatk@gmail.com', 'maha2006@'))
