import time

import params as p
import requests
import re
import db_actions as db_a

vk_token = p.vk_token  # test token
r_p = p.req_params


class UserVK:
    def __init__(self, uid):
        self.id = uid
        usr = self.get_user(self.id)
        self.names = usr['first_name'] + ' ' + usr['last_name']
        self.sex = usr['sex']  # 2-M, 1-F ,0-Not
        if usr.get('bdate'):
            self.bdate = usr['bdate']
        else:
            self.bdate = None
        if usr.get('city'):
            self.city = usr['city']['id']
        else:
            self.city = 1
            print('У пользователя не указан город, будем искать по Москве')
        if usr.get('interests'):
            self.interests = usr['interests']
        else:
            self.interests = None
        if usr.get('music'):
            self.music = usr['music']
        else:
            self.music = None
        if usr.get('books'):
            self.books = usr['books']
        else:
            self.books = None
        self.friends = get_friends(self.id)
        self.groups = get_groups(self.id)  # list(ids)

    def get_user(self, uid):
        params = r_p
        params['user_ids'] = uid,
        params['fields'] = 'sex,bdate,city,home_town,interests,music,books'
        response = requests.get('https://api.vk.com/method/users.get', params)
        resp = response.json()['response'][0]
        return resp


def get_groups(uid):
    params = r_p
    params['user_id'] = uid
    response = requests.get('https://api.vk.com/method/groups.get', params)
    user_groups = None
    if response.json().get('response'):
        user_groups = response.json()['response']['items']
    return user_groups


def get_friends(uid):
    params = r_p
    params['user_id'] = uid
    response = requests.get('https://api.vk.com/method/friends.get', params)
    user_friends = None
    if response.json().get('response'):
        user_friends = response.json()['response']['items']
    return user_friends


def get_etoken(url_token):
    pattern = re.compile('(\S*)(access_token=)(\w*)(\S*)')
    token = pattern.sub(r'\3', url_token)


def get_uid(user_uid):
    res_uid = user_uid.strip().split(',')[0]
    return res_uid


def check_user(uid):
    params = r_p
    params['user_ids'] = uid
    response = requests.get('https://api.vk.com/method/users.get', params)
    resp = response.json()
    if resp.get('response'):
        user_deactivated = resp['response'][0].get('deactivated')
        if user_deactivated:
            return user_deactivated
        else:
            return resp['response'][0]['id']
    elif resp.get('error'):
        return 'error_code:' + str(resp['error']['error_code'])


def search_candidate(user_vk):
    params = r_p
    params['count'] = 100  # VK limit 1000
    sex = 0
    if user_vk.sex == 2:
        sex = 1
    elif user_vk.sex == 1:
        sex = 2
    params['sex'] = sex
    params['age_from'] = p.age_min
    params['age_to'] = p.age_max
    params['city'] = user_vk.city
    params['fields'] = 'interests,music,books'
    params['has_photo'] = 1
    response = requests.get('https://api.vk.com/method/users.search', params)
    candidates = response.json()['response']['items']
    return candidates


def check_mutual_friends(c_id):
    params = r_p
    params['source_uid'] = user_vk.id
    params['target_uid'] = c_id
    time.sleep(1 / 3)
    response = requests.get('https://api.vk.com/method/friends.getMutual', params)
    resp = response.json()['response']
    res = False
    if len(resp):
        res = True
    return res

def get_mutual_friends(c_list):
    friends_groups_set = set()
    counter = 0
    t_counter = len(c_list)
    temp_list = list()
    params = r_p
    res_friend_dict = dict()
    res_groups_dict = dict()
    res_photos_dict = dict()
    for item in c_list:
        counter += 1
        t_counter -= 1
        temp_list.append(item['id'])
        if counter == 25 or t_counter == 0:
            friend_dict = dict()
            groups_dict = dict()
            # params['code'] = f'var a = 0; var b =  {temp_list}; var s = "{{"; var sid = {user_vk.id}; while (a != {len(temp_list)})' + '{s = s + b[a] +": "+API.friends.getMutual({"source_uid":sid,"target_uid":b[a]}).length+", "; a = a + 1;}; return s+"}"; '
            # response = requests.post('https://api.vk.com/method/execute', params)
            # friend_dict = eval(response.json()['response'])
            # res_friend_dict.update(friend_dict)
            time.sleep(1 / 3)
            # params['code'] = f'var a = 0; var b =  {temp_list}; var s = "{{"; while (a != {len(temp_list)})' + '{s = s + b[a] +": ["+API.groups.get({"user_uid":b[a]}).items+"], "; a = a + 1;}; return s+"}"; '
            # response = requests.post('https://api.vk.com/method/execute', params)
            # # print(response.json())
            # groups_dict = eval(response.json()['response'])
            # res_groups_dict.update(groups_dict)
            # time.sleep(1 / 3)
            params['code'] = f'var a = 0; var b =  {temp_list}; var s = "{{"; while (a != {len(temp_list)})' + '{s = s + b[a] +": ' \
                            '["+API.photos.get({"owner_id":b[a],"album_id":"profile","extended":1})+"], "; a = a + 1;}; ' \
                            'return s+"}"; '
            response = requests.post('https://api.vk.com/method/execute', params)
            print(response.json())
            photos_dict = eval(response.json()['response'])
            res_photos_dict.update(photos_dict)

            # print(response.json())
            counter = 0
            temp_list.clear()

            # print('*', end='')
    # print('res_friend_dict=', res_friend_dict)
    # print('res_groups_dic=', res_groups_dict)
    print('res_photos_dic=', res_photos_dict)
    # response_set = set()
    # for str_item in response_list:
    #     if str_item != '':
    #         response_set.add(int(str_item))
    # friends_groups_set = friends_groups_set | response_set
    # print()
    return friends_groups_set


def check_mutual_groups(c_id):
    source_groups = set(user_vk.groups)
    target_groups = set()
    if get_groups(c_id):
        target_groups = set(get_groups(c_id))
    res = True
    if source_groups.isdisjoint(target_groups):
        res = False
    return res


def get_photos(c_id):
    params = r_p
    params['owner_id'] = c_id
    params['album_id'] = 'profile'
    response = requests.get('https://api.vk.com/method/photos.get', params)
    resp = response.json()
    print('resp_photos=', resp)


def clean_candidates(items):
    clear_list = list()
    for item in items:
        if item['is_closed']:
            # items.remove(item)
            continue
        else:
            del item['is_closed']
            del item['can_access_closed']
            del item['track_code']
            item['used'] = False
            item['m_friends'] = False
            item['m_groups'] = False
            clear_list.append(item)
    return clear_list




if __name__ == '__main__':  # armo.appacha,24863449,27406252,10754162,d.lonkin,o.sevostyanova77,eshmargunov
    user_vk = UserVK(24863449)
    dirty_candidates = search_candidate(user_vk)
    print(len(dirty_candidates))
    candidates = clean_candidates(dirty_candidates)
    get_mutual_friends(candidates)
    print(len(candidates))
    # for candidate in candidates['items']:
    #     vk_id = candidate['id']
    #     used = False
    #     m_friends = check_mutual_friends(vk_id)
    #     m_groups = check_mutual_groups(vk_id)
    #     if candidate.get('interests'):
    #         interests = candidate['interests']
    #         music = candidate['music']
    #         books = candidate['books']
    #     else:
    #         continue
    #     photos = get_photos(vk_id)
        # db_a.add_candidate(vk_id, used, m_friends, m_groups, interests, music, books, photos)

    # print(user_vk.friends)
    # print(user_vk.city)
    # print(find_friends(user_vk))
    # print('Для использования приложения необходим ключ авторизации')
    # print('перейдите по ссылке: ')
    # print(p.req_access_key)
    # print('Подтвердите разрешения для приложения')
    # print('После перехода на пустую страницу с текстом: "Пожалуйста, не копируйте данные из адресной строки для '
    #       'сторонних сайтов. Таким образом Вы можете потерять доступ к Вашему аккаунту."')
    # token_url = input('полностью скопируйте её адрес и введите его сюда => ')
    # vk_token = get_etoken(token_url)

    # input_id = input('Введите id пользователя ВК или его имя: ')
    # user_uid = get_uid(input_id)
    # user_id = check_user(user_uid)
    # if user_id == 'error_code:113':
    #     print(f'Пользователь "{user_uid}" не найден. Проверьте вводимые данные.')
    # elif user_id == 'error_code:5':
    #     print('Ошибка авторизации, проверьте eToken')
    # elif user_id == 'many':
    #     print(f'По вашему запросу: "{user_uid}" найдено несколько пользователей. Уточните имя.')
    # elif user_id == 'banned':
    #     print(f'Пользователь "{user_uid}" заблокирован. Анализ невозможен.')
    # elif user_id == 'deleted':
    #     print(f'Пользователь "{user_uid}" удалён либо не существует. Анализ невозможен.')
    # else:
    #     print(f'Пользователь "{user_uid}" (id{user_id}) доступен для анализа ...')
