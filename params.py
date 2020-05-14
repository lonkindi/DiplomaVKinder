req_access_key = 'https://oauth.vk.com/authorize?client_id=7331927&display=page&redirect_uri=https://oauth.vk.com' \
                 '/blank.html&scope=friends,offline&response_type=token&v=5.103&state=VKinder&revoke=1 '

vk_token = '0292b075b7edbcefe76d6574bf2bfb0d40f4eb1dcd6ae754464f8fe9100ac548cc28ae2fc062e5e2e694d'

req_params = dict(
        access_token=vk_token,
        v='5.103')

weights = [
    ("sex", 1),
    ("city", 2),
    ("friends", 3),
    ("age", 4),
    ("groups", 5),
    ("interests", 6),
    ("music", 7),
    ("books", 8),
]

age_min = 45
age_max = 45

