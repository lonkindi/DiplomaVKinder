req_access_key = 'https://oauth.vk.com/authorize?client_id=7331927&display=page&redirect_uri=https://oauth.vk.com' \
                 '/blank.html&scope=friends,offline&response_type=token&v=5.103&state=VKinder&revoke=1 '

vk_token = '0292b075b7edbcefe76d6574bf2bfb0d40f4eb1dcd6ae754464f8fe9100ac548cc28ae2fc062e5e2e694___'  # для отладки

req_params = dict(
    access_token=vk_token,
    v='5.107')

weights = [
    ("sex", 8),
    ("city", 7),
    ("friends", 6),
    ("age", 5),
    ("groups", 4),
    ("interests", 3),
    ("music", 2),
    ("books", 1)
]

age_min = 18
age_max = 19
