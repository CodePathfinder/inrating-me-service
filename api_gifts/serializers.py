from . models import UserSettings, Images, Places, AdFilters, UserTutorial, UserPrivacySettings


def me_serialize(user):
    user_settings = UserSettings.objects.get(user_id=user.id)
    avatar_image = Images.objects.get(author_id=user.id)
    place = Places.objects.get(id=user_settings.geo_id)
    tutorial = UserTutorial.objects.get(user_id=user.id)

    try:
        ad_filters = AdFilters.objects.get(user_id=user.id)
        social_statuses = ad_filters.social_statuses
        activity_statuses = ad_filters.activity_statuses
    except AdFilters.DoesNotExist:
        social_statuses = []
        activity_statuses = []

    try:
        privacy_settings = UserPrivacySettings.objects.get(user_id=user.id)
        profile = privacy_settings.profile
        subscribers = privacy_settings.subscribers
        subscriptions = privacy_settings.subscriptions
        subscribe = privacy_settings.subscribe
        chat = privacy_settings.chat
    except UserPrivacySettings.DoesNotExist:
        profile = "all"
        subscribers = "all"
        subscriptions = "all"
        subscribe = "all"
        chat = "all"

    return {
        "id": user.id,
        "nickname": user.nickname,
        # "active_gift": null,
        "avatar_image": {
            "id": avatar_image.id,
            "author_id": avatar_image.author_id,
            "url": avatar_image.url,
            "url_large": avatar_image.url_large,
            "url_medium": avatar_image.url_medium,
            "url_small": avatar_image.url_small,
            "server_id": avatar_image.server_id,
            "url_origin": avatar_image.url_origin,
            "url_large_origin": avatar_image.url_large_origin,
            "url_medium_origin": avatar_image.url_medium_origin,
            "url_small_origin": avatar_image.url_small_origin,
            "tag": avatar_image.tag,
            "group_id": avatar_image.group_id,
            "url_shape_cropped_round": avatar_image.url_shape_cropped_round,
            "url_shape_cropped_star": avatar_image.url_shape_cropped_star,
            "url_shape_cropped_diamond": avatar_image.url_shape_cropped_diamond
        },
        # "is_commercial": false,
        # "off_page": false,
        "name": user.name,
        "lastname": user.lastname,
        "status": user.status,
        # "is_subscribed": false,
        # "is_online": false,
        # # "rating": {
        # #     "level": 1,
        # #     "value": 1,
        # #     "caption": 1,
        # #     "proportion": 0.0141
        # # },
        # "comments": "all",

        "geo_id": {
            "id": place.id,
            "google_place_id": place.google_place_id,
            "location": get_location(user_settings.lang, place),
            "lat": place.lat,
            "lng": place.lng,
            "locality": place.locality,
            "country": place.country,
            "administrative_area_level_1": place.administrative_area_level_1,
            "administrative_area_level_2": place.administrative_area_level_2,
            # "address_components": [?]
        },
        # "contest_entry_instance": null,
        "chat_main_lang": user_settings.chat_main_lang,
        # "is_voted": false,
        "email": user.email,
        "phone": user.phone,
        "gender": user.gender,
        "background_image": user.background_image_id,
        "birth_date": str(user.birth_date),
        "birth_date_timestamp": user.get_dob_timestamp,
        # # "typed_rating": {
        # #     "day": 0,
        # #     "day_caption": 0,
        # #     "week": 1,
        # #     "week_caption": 1,
        # #     "month": 1,
        # #     "month_caption": 1
        # # },
        "personal_status": user_settings.personal_status,
        "family_status": user_settings.family_status,
        "social_links": user_settings.social_links,
        # # "contest_entry": null,
        # # "is_verified": false,
        # # "is_chined": false,
        # # "is_active_story": false,
        # # "is_story_seen": true,
        "social_statuses": social_statuses,
        "activity_statuses": activity_statuses,
        # # "offers_count": 0,
        # # "posts_count": 1,
        # # "subscriptions_count": 1,
        # # "subscribers_count": 0,
        # # "bookmarks_count": 0,
        # # "mentions_count": 0,
        "settings": {
            "lang": user_settings.lang,
            "chat_langs": {
                "main_lang": user_settings.chat_main_lang,
                "sub_langs": user_settings.chat_sub_langs,
            },
            "chat_autotranslate": user_settings.chat_autotranslate,
            "sounds": user_settings.sounds
        },
        "tutorial": {
            "user_id": tutorial.user_id,
            "web_mobile": tutorial.web_mobile,
            "web_desktop": tutorial.web_desktop,
            "android": tutorial.android,
            "ios": tutorial.ios
        },
        # # "subscribe_requests_count": 0,
        # # "gift_bg_available": false,
        # # "location": null,
        # # "temp_status": null,
        "privacy_settings": {
            "profile": profile,
            "subscribers": subscribers,
            "subscriptions": subscriptions,
            "subscribe": subscribe,
            "chat": chat
        }
    }


def get_location(lang, place):
    """ get location colomn (uk, ru, or en) depending on user's main language """

    if lang == 'uk':
        location = place.uk
    elif lang == 'ru':
        location = place.ru
    elif lang == 'en':
        location = place.en
    else:
        location = place.en
    return location
