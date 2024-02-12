import requests

user_acces_token_and_id = {}

def login(email , password):
    url = 'http://158.160.9.246/api/login/'
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
    url = 'http://158.160.9.246/api/profiles/'

    response = requests.get(url)
    result = ''
    if response.status_code == 200:
        for response in response.json():
            bio = response.get("bio") if response.get("bio") else 'Нету биографии'
            user_post_count = f"Количество постов этого пользователя равен {len(response.get('user_posts'))}" if response.get('user_posts') else 'У этого пользователья ещё нету постов'
                    
            result += f'\n \nПрофиль пользователья {response.get("last_name")}\nимя: {response.get("username")} \nФамилия: {response.get("last_name")} \nБиография: {bio}\n{user_post_count}'
        return result
    else:
        return 'Не найдено профилей' 
    
def my_profile(bearer_token):
    url = 'http://158.160.9.246/api/profiles/my_profile/'
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response = response.json()
        result = ''
        bio = response.get("bio") if response.get("bio") else 'Нету биографии'
        user_post_count = f"Количество твоих постов равен {len(response.get('user_posts'))}" 

        result += f'\n \nЭто ваш профиль в twitter_hackaton {response.get("last_name")}\n \nимя: {response.get("username")} \nФамилия: {response.get("last_name")} \nБиография: {bio}\n{user_post_count}'

        return result
    elif response.status_code == 401:
            return 401
    else:
        return None


def feeds(bearer_token):
    url = 'http://158.160.9.246/api/feeds/'
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response = response.json()
        posts = []
        for post in response:
            image = {'image': post.get('image')}
            result = {'post': f'Автор этого поста {post.get("username")}\n {post.get("text")}\n Комментарии на этот пост: {post.get("comment")}\n Дата публикации: {post.get("pub_date")}'}
            posts.append({**image, **result}) 
        return posts
    elif response.status_code == 401:
            return 401
    else:
        return None


def posts():
    url = 'http://158.160.9.246/api/posts/'
    result = []

    while url:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for post in data.get('results'):
                image = {'image': post.get('image')}
                comment = post.get('comments')
                res = ''
                if comment:
                    for comm in comment:
                        res = f"{comm.get('text')},\n"
                content = {'content': f"{post.get('text')}\nавтор этого поста {post.get('author_username')}\nКоличество лайков {post.get('like_count')}\n\nДата публикации {post.get('pub_date')}\nКомментарии {res}"}
                result.append({**image, **content})


            url = data.get('next')
    return result



def my_favorites(bearer_token):
    url = 'http://158.160.9.246/api/my_favorites/'
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    response = requests.get(url, headers=headers)
    if isinstance(response.json(), str):
        return None
    elif response.status_code == 200:
        response = response.json()
        posts = []
        if response is not []:
            for post in response:
                fovorite_post = post.get('post')
                if fovorite_post:
                    image = {'image': post.get('image')}
                    comment = fovorite_post.get('comments')
                    fov_comm = []
                    res = ''
                    if comment:
                        for comm in comment:
                            res = f"{comm.get('text')},\n"
                            fov_comm.append('res')
                    result = {'post': f"Избранный\nАвтор этого поста {fovorite_post.get('author_username')}\n{fovorite_post.get('text')}\nКоличество лайков {fovorite_post.get('like_count')}\nКоментарии на этого постa {res}"}
                    posts.append({**image, **result}) 
            return posts
        else:
            return None
    elif response.status_code == 401:
        return 401
    else:
        return None


def recomendation(bearer_token):
    url = 'http://158.160.9.246/api/recomendation/'
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    response = requests.get(url, headers=headers)
    result = []

    if response.status_code == 200:
        response = response.json()
        result = []
        if isinstance(response, list):
            for post in response:
                image = {'image': post.get('image')}
                content = {'content': f"{post.get('text')}\nавтор этого поста {post.get('author_username')}\nДата публикации {post.get('pub_date')}"}
                result.append({**image, **content})
                
            return result
        else:
            return None
    elif response.status_code == 401:
        return 401
    else:
        return None


def exit(message_id):
    try:
        user_acces_token_and_id.pop(message_id)
        return 'Успешно вышли с аккаунта'
    except:
        return 'Чтобы выйти из аккаунта,сперва надо авторизоваться.\nМожете авторизоваться /login'