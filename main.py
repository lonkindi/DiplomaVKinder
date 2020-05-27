import datetime
import random

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
        if usr.get('bdate'): # Если возраст пользователя скрыт, то берём из настроек приложения свои данные
            self.bdate = usr['bdate']
        else:
            print('У пользователя не указан возраст. Ограничение по возрасту будет взято из настроек программы.')
            self.bdate = None
        if usr.get('city'): # Если город не указан, то ищем в столице
            self.city = usr['city']['id']
        else:
            self.city = 1
            print('У пользователя не указан город, будем искать по Москве')
        if usr.get('interests'):
            self.interests = parse_text(usr['interests'])
        else:
            self.interests = None
        if usr.get('music'):
            self.music = parse_text(usr['music'])
        else:
            self.music = None
        if usr.get('books'):
            self.books = parse_text(usr['books'])
        else:
            self.books = None
        self.friends = get_friends(self.id)  # list(ids)
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
        user_friends = list()
        for item in response.json()['response']['items']:
            user_friends.append(item['id'])
    return user_friends


def get_etoken(url_token):
    pattern = re.compile('(\S*)(access_token=)(\w*)(\S*)')
    token = pattern.sub(r'\3', url_token)
    return token


def get_uid(user_uid):
    res_uid = user_uid.strip().split(',')[0]
    return res_uid


def parse_text(string):
    result = re.split(r'[;,]\s', string)
    return set(result)


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


def search_candidate(params):
    response = requests.get('https://api.vk.com/method/users.search', params)
    candidates = response.json()['response']['items']
    return candidates


def get_age(b_date):
    d1 = datetime.datetime.strptime(b_date, '%d.%m.%Y').date()
    d2 = datetime.datetime.now().date()
    delta = d2 - d1
    return delta.days//365


def get_friends_groups_photos(c_list):
    counter = 0
    t_counter = len(c_list)
    temp_list = list()
    params = r_p
    res_friends_dict = dict()
    res_groups_dict = dict()
    res_photos_dict = dict()
    print('Запросы к API VK ', end='')
    for item in c_list:
        counter += 1
        t_counter -= 1
        temp_list.append(item['id'])
        if counter == 25 or t_counter == 0:
            print('~', end='')
            params['code'] = f'var a = 0; var b =  {temp_list}; var s = "{{"; var sid = {user_vk.id}; ' \
                             f'while (a != {len(temp_list)})' + '{s = s + b[a] +": "+API.friends.getMutual' \
                                                                '({"source_uid":sid,"target_uid":b[a]}).length' \
                                                                '+", "; a = a + 1;};\
                                return s+"}"; '
            response = requests.post('https://api.vk.com/method/execute', params)
            friend_dict = eval(response.json()['response'])
            res_friends_dict.update(friend_dict)
            print('~', end='')
            params['code'] = f'var a = 0; var b =  {temp_list}; var s = "{{"; while (a != {len(temp_list)})' \
                             + '{s = s + b[a] + ": ["+API.groups.get({"user_id":b[a]}).items+"], "; ' \
                               'a = a + 1;}; return s+"}"; '
            response = requests.post('https://api.vk.com/method/execute', params)
            groups_dict = eval(response.json()['response'])
            res_groups_dict.update(groups_dict)
            print('~', end='')

            # for i in temp_list:
            #     res_photos_dict[i] = random.randint(0, 4)

            params['code'] = f'var a = 0; var b =  {temp_list}; var s = "{{"; while (a != {len(temp_list)})' \
                             + '{s = s + b[a] +": "+API.photos.get({"owner_id":b[a],"album_id":"profile"}).count' \
                               '+", "; a = a + 1;}; ' \
                               'return s+"}"; '
            response = requests.post('https://api.vk.com/method/execute', params)
            print('response=', response.text)
            photos_dict = eval(response.json()['response'])
            res_photos_dict.update(photos_dict)

            counter = 0
            temp_list.clear()
    print()
    return res_friends_dict, res_groups_dict, res_photos_dict


def update_candidates(candidates, friends_dict, groups_dict, photos_dict):
    res_candidates = list()
    for item in candidates:
        if photos_dict[item['id']] > 2:
            item['photos'] = photos_dict[item['id']]
            if friends_dict[item['id']]:
                item['m_friends'] = True
            groups_set = set(groups_dict[item['id']])
            user_friends_set = set(user_vk.friends)
            if not groups_set.isdisjoint(user_friends_set):
                item['m_groups'] = True
            res_candidates.append(item)
    return res_candidates


def comb_candidates(items):
    clear_list = list()
    for item in items:
        if item['is_closed']:
            continue
        else:
            del item['is_closed']
            del item['can_access_closed']
            del item['track_code']
            item['used'] = False
            item['m_friends'] = False
            item['m_groups'] = False
            item['photos'] = 0

            if not item.get('interests'):
                item['interests'] = ''
            item['interests'] = parse_text(item['interests'])
            m_interests = check_sets(item['interests'], user_vk.interests)
            if m_interests:
                item['interests'] = True
            else:
                item['interests'] = False

            if not item.get('music'):
                item['music'] = ''
            item['music'] = parse_text(item['music'])
            m_music = check_sets(item['music'], user_vk.music)
            if m_music:
                item['music'] = True
            else:
                item['music'] = False
            if not item.get('books'):
                item['books'] = ''
            item['books'] = parse_text(item['books'])
            m_books = check_sets(item['books'], user_vk.books)
            if m_books:
                item['books'] = True
            else:
                item['books'] = False
            clear_list.append(item)
    return clear_list

def get_weights():
    weights = p.weights
    weights.sort(key=lambda i: i[1])
    weights_lst = list()
    for item in weights:
        weights_lst.append(item[0])
    return weights_lst

def check_sets(set1, set2):
    r_set = set1 & set2
    return r_set


def check_friends(candidates):
    res_candidates = list()
    for item in candidates:
        if item['m_friends']:
            res_candidates.append(item)
    return res_candidates

def check_groups(candidates):
    res_candidates = list()
    for item in candidates:
        if item['m_groups']:
            res_candidates.append(item)
    return res_candidates

def check_interests(candidates):
    res_candidates = list()
    for item in candidates:
        if item['interests']:
            res_candidates.append(item)
    return res_candidates

def check_music(candidates):
    res_candidates = list()
    for item in candidates:
        if item['music']:
            res_candidates.append(item)
    return res_candidates

def check_books(candidates):
    res_candidates = list()
    for item in candidates:
        if item['books']:
            res_candidates.append(item)
    return res_candidates

def get_photos(candidates):
    pass

def check_used(candidates):
    res_candidates = list()
    used_list = db_a.get_used(user_vk.id)
    for item in candidates:
        if not item['id'] in used_list:
            res_candidates.append(item)
    return res_candidates

if __name__ == '__main__':  # armo.appacha,24863449,27406252,10754162,d.lonkin,o.sevostyanova77,eshmargunov
    user_vk = UserVK(24863449)

    params = r_p
    params['count'] = 100  # VK limit 1000
    sex = 0
    if user_vk.sex == 2:
        sex = 1
    elif user_vk.sex == 1:
        sex = 2
    params['sex'] = sex
    if user_vk.bdate:
        age = get_age(user_vk.bdate)
        min, max = age, age
    else:
        min, max = p.age_min, p.age_max
    params['age_from'] = min
    params['age_to'] = max
    params['city'] = user_vk.city
    params['fields'] = 'interests,music,books'
    params['has_photo'] = 1
    weights = get_weights()
    # weights.insert(0,0)
    # print(weights)

    for i in range(0,8):
        print(weights)
        # print('weights1=', weights)
        # weights.remove(item)
        # print('weights2=', weights)
        # print('item = ', item)
        if not 'sex' in weights:
            params['sex'] = ''
        if not 'city' in weights:
            params['city'] = ''
        if not 'age' in weights:
            params['age_from'] = ''
            params['age_to'] = ''
        # elif item[0] == 'city':
        #     params['city'] = ''
        dirty_candidates = search_candidate(params)
        print('dirty_candidates = ', len(dirty_candidates))
        candidates = comb_candidates(dirty_candidates)
        print('comb_candidates = ', len(candidates))
        friends_dict, groups_dict, photos_dict = get_friends_groups_photos(candidates)
        candidates_list = update_candidates(candidates, friends_dict, groups_dict, photos_dict)
        print('candidates_list = ', len(candidates_list))
        # if len(candidates_list) < 3:
        #     continue
        if 'friends' in weights:
            candidates = check_friends(candidates_list)
            print('f_candidates =', len(candidates))
            # if len(candidates) < 3:
            #     continue
        if 'groups' in weights:
            candidates = check_groups(candidates)
            print('g_candidates =', len(candidates))
            # if len(candidates) < 3:
            #     continue
        if 'interests' in weights:
            candidates = check_interests(candidates)
            print('i_candidates =', len(candidates))
        if 'music' in weights:
            candidates = check_music(candidates)
            print('m_candidates =', len(candidates))
        if 'books' in weights:
            candidates = check_books(candidates)
            print('b_candidates =', len(candidates))
        candidates = check_used(candidates)
        if len(candidates) >= 3:
            print('len result = ', len(candidates))
            print ('result = ', candidates)
            break
        else:
            weights[i] = 0

        # print('check_friends=', len(check_friends(candidates_list)))



        # friends_dict, groups_dict, photos_dict = get_friends_groups_photos(candidates)
        # candidates_list = update_candidates(candidates, friends_dict, groups_dict, photos_dict)
        # print('candidates_list = ', len(candidates_list))
        # break

    # dirty_candidates = search_candidate(params)
    # # print(dirty_candidates)
    # candidates = comb_candidates(dirty_candidates)
    # print(candidates)
    # friends_dict, groups_dict, photos_dict = get_friends_groups_photos(candidates)
    # print('friends_dict=', friends_dict)
    # print('groups_dict=', groups_dict)
    # print('photos_dict=', photos_dict)
    # print(update_candidates(candidates, friends_dict, groups_dict, photos_dict))
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
    # print(get_age("26.12.1976"))



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
