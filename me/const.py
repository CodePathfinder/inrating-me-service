import pytz


imageDefault = {
    "id": 0,
    "url": 'https://media.inrating.top/storage/img/default/default-avatar.jpg',
    "url_large": 'https://media.inrating.top/storage/img/default/default-avatar_large.jpg',
    "url_medium": 'https://media.inrating.top/storage/img/default/default-avatar_medium.jpg',
    "url_small": 'https://media.inrating.top/storage/img/default/default-avatar_small.jpg',
    "mentioned_users_count": 0
}

inratingAccountID = 1733

postTypes = {
    'user-post': 1,
    'group-post': 2,
    'album-post': 3,
    'story-post': 4,
    'group-video-post': 5,
    'from-group-post': 6,
    'exchange-post': 7
}

locationLanguages = {
    'en': 'en',  # english
    'ru': 'ru',  # russian
    'uk': 'uk',  # ukrainian
}

default_privacy_settings = {
    "profile": "all",
    "subscribers": "all",
    "subscriptions": "all",
    "subscribe": "all",
    "chat": "all"
}

kiev_tz = pytz.timezone('Europe/Kiev')
