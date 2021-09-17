from datetime import datetime, date, timedelta
from django.db.models import Sum, Q
from django.core.cache import cache
from math import sqrt
import requests
from microservices.settings import GOOGLE_PLACES_API_KEY, GOOGLE_API_PLACE_DETAILS_URL

from .models import Users, UserSettings, Images, Places, UserPrivacySettings, CommercialButtons, ChinChins, ReportedPosts, GiftUser, Gifts, TempStatuses, FieldOfActivityDictionary, SocialStatusDictionary, Offers, PostViews
from .serializers import ImagesSerializer
from . import const


# def print_result_decorator(func):
#     def print_action(*args, **kwargs):
#         start = datetime.now()
#         result = func(*args, **kwargs)
#         end = datetime.now()
#         print()
#         print(f'Function "{func.__name__}" returns: {result}')
#         print(f'Performance time = ', end - start)
#         print()
#         return result
#     return print_action


def get_response_data(uid, cuid):

    user = Users.objects.select_related('avatar_image', 'background_image', 'commercialbuttons', 'commercialinfo',
                                        'tempstatuses', 'useradditionalinfo', 'userprivacysettings', 'usersettings', 'usertutorial').get(id=uid)
    user_settings = user.usersettings
    additional_info = user.useradditionalinfo
    avatar_image = get_avatar_image_resource(user)
    is_commercial = user.parent_id != None
    is_personal_profile = cuid == uid
    active_ads_count = user.ads_set.filter(active=True).count()
    is_active_story = get_is_active_story(user, cuid)
    contest_resource = get_contest_resource(user)

    # uncomment to see all cached keys
    # for k in cache.keys('*'):
    #     print(k)

    main_resource = {
        "id": user.id,
        "nickname": user.nickname,
        "active_gift": get_gift_resource(user),
        "avatar_image": avatar_image,
        "is_commercial": is_commercial,
        "off_page": user.id == const.inratingAccountID,
        "name": user.name if user.name else user.nickname,
        "lastname": user.lastname if user.lastname else "",
        "status": user.status,
        "is_subscribed": is_subscribed(user, cuid),
        "is_online": is_online(user),
        "rating": get_rating(user),
        "comments": user_settings.comments if user_settings.comments else "all",
        "contest_entry_instance": contest_resource,
        "geo_id": get_place_resource(user_settings, cuid) if user_settings and user_settings.geo_id else None,
        "chat_main_lang": user_settings.chat_main_lang if user_settings.chat_main_lang else 'ru',
        "is_voted": is_voted(user, cuid),
        "is_commercial": is_commercial,
        "active_ads_count": active_ads_count if active_ads_count else 0,
        "gender": user.gender,
        "background_image": get_background_image_resource(user),
        "birth_date": str(user.birth_date) if user.birth_date else user.birth_date,
        "birth_date_timestamp": get_timestamp_from_date(user.birth_date) if user.birth_date else user.birth_date,
        "typed_rating": get_typed_rating(user),
        "personal_status": user_settings.personal_status,
        "family_status": user_settings.family_status,
        "social_links": user_settings.social_links if user_settings.social_links else [],
        "contest_entry": contest_resource['slug'] if contest_resource else None,
        "is_verified": additional_info.phone_verified if additional_info.phone_verified else False,
        "is_chined": is_chin_chined(user, cuid),
        "is_active_story": True if is_active_story else False,
        "is_story_seen": is_story_seen(user, cuid) == is_active_story,
        "social_statuses": get_social_statuses(user),
        "activity_statuses": get_activity_statuses(user),
        "offers_count": count_offers(user) if is_commercial else 0,
        "posts_count": user.posts_set.filter(type=const.postTypes['user-post'], deleted_at__isnull=True).count(),
        "subscriptions_count": follow(user),
        "subscribers_count": followers(user),
        "location": get_location(additional_info),
        "temp_status": get_temp_status_resourse(user),
        "privacy_settings": get_user_privacy_settings_resource(user)
    }
    # add me specific info to main_resource (dict)
    if is_personal_profile:
        main_resource.update(add_personal_info(user, user_settings))
    # merge commercial info (dict) with main_resource (dict)
    if is_commercial:
        main_resource.update(get_commercial_info(user))

    return main_resource


def get_avatar_image_resource(user):

    key = f'cached-avatar-image-.{user.id}'
    if cache.has_key(key):
        avatar_image = cache.get(key)

    else:
        try:
            avtr_image = user.avatar_image
        except Images.DoesNotExist:
            avatar_image = const.imageDefault
        else:
            serializer = ImagesSerializer(avtr_image)
            avatar_image = serializer.data
            if not avatar_image['url_origin']:
                avatar_image['url_origin'] = avatar_image['url']
                avatar_image['url_small_origin'] = avatar_image['url']
                avatar_image['url_medium_origin'] = avatar_image['url']
                avatar_image['url_large_origin'] = avatar_image['url']
            avatar_image['mentioned_users_count'] = mentioned_users(avtr_image)
            cache.set(key, avatar_image)

    return avatar_image


def mentioned_users(image):
    mentioned_users = image.mentions_set.filter(deleted_at__isnull=True)
    return mentioned_users.count() if mentioned_users else 0


def get_user_privacy_settings_resource(user):
    try:
        settings = user.userprivacysettings
        return {
            "profile": settings.profile,
            "subscribers": settings.subscribers,
            "subscriptions": settings.subscriptions,
            "subscribe": settings.subscribe,
            "chat": settings.chat
        }
    except UserPrivacySettings.DoesNotExist:
        return const.default_privacy_settings


def get_location_place_resource(cuid, place):
    # get location colomn (uk, ru, or en) depending on user's main language
    current_user_settings = UserSettings.objects.get(user_id=cuid)
    if current_user_settings.lang == const.locationLanguages['uk']:
        location = place.uk
    elif current_user_settings.lang == const.locationLanguages['ru']:
        location = place.ru
    elif current_user_settings.lang == const.locationLanguages['en']:
        location = place.en
    else:
        location = place.en
    return location


def get_place_resource(user_settings, cuid):
    try:
        place = Places.objects.get(id=user_settings.geo_id)
        place_resource = {
            "id": place.id,
            "google_place_id": place.google_place_id,
            "location": get_location_place_resource(cuid, place),
            "lat": place.lat,
            "lng": place.lng,
            "locality": place.locality,
            "country": place.country,
            "administrative_area_level_1": place.administrative_area_level_1,
            "administrative_area_level_2": place.administrative_area_level_2,
            # "address_components": get_address_components(place.google_place_id, user_settings.lang)
        }
        return place_resource
    except Places.DoesNotExist:
        return None


def get_contest_resource(user):

    contest_user = user.contestsusers_set.filter(status='participant', deleted_at__isnull=True).order_by(
        '-contest__id').filter(contest__end_date__gte=datetime.now(), contest__start_date__lte=datetime.now()).first()

    if contest_user:
        contest_entry = contest_user.contest
        contest_short_resource = {
            "id": contest_entry.id,
            "name": contest_entry.name,
            "slug": contest_entry.slug,
        }
        return contest_short_resource
    else:
        return None


def is_voted(user, cuid):

    key = f'user-.{user.id}.-voted-by-.{cuid}'
    if cache.has_key(key):
        is_voted = cache.get(key)
    else:
        votes = user.userextrarate_set.filter(sender_id=cuid, type=1).filter(
            created_at__gte=datetime.now(const.kiev_tz).date()).order_by('-created_at')
        is_voted = votes.exists()
        cache.set(key, is_voted)

    return is_voted


def get_categories(user):
    categories = user.commercialcategoryuser_set.all()
    categories_list = [category.category.name for category in categories]
    return categories_list


def get_commercial_button_resource(user):
    try:
        type = user.commercialbuttons.type
        value = user.commercialbuttons.value
        return {
            "type": type if type else None,
            "value": value if value else None
        }
    except CommercialButtons.DoesNotExist:
        return None


def get_commercial_info(user):

    return {
        "email": user.email,
        "phone": user.phone,
        "site": user.commercialinfo.site if user.commercialinfo.site else None,
        "desc": user.commercialinfo.desc if user.commercialinfo.desc else None,
        "categories": get_categories(user) if get_categories(user) else None,
        "button": get_commercial_button_resource(user),
    }


def get_typed_rating(user):
    # get user's rating data from cache, if not available - retrieve from DB
    key = f'typed-rating-.{user.id}'
    if cache.has_key(key):
        rating = cache.get(key)
    else:
        rating = typed_rating(user)
        timeout = (tomorrow() - datetime.now()).total_seconds()
        cache.set(key, rating, int(timeout))
    return rating


def typed_rating(user):
    # Retrive user's rating data from DB

    # configuration of timepoints
    t = date.today()
    w = t - timedelta(days=t.isoweekday())
    today = datetime(t.year, t.month, t.day)
    start_of_week = datetime(w.year, w.month, w.day)
    start_of_month = datetime(t.year, t.month, day=1)

    # get user's day rating
    day_query = user.rating_set.filter(deleted_at__isnull=True, created_at__range=(
        today, datetime.now())).values('user_id').annotate(rating_day=Sum('rating'))

    if day_query:
        rating_day = int(day_query[0]['rating_day'])
    else:
        rating_day = 0

    # get user's week rating
    week_query = user.rating_set.filter(deleted_at__isnull=True, created_at__gte=start_of_week,
                                        created_at__lte=datetime.now()).values('user_id').annotate(rating_week=Sum('rating'))
    if week_query:
        rating_week = int(week_query[0]['rating_week'])
    else:
        rating_week = 0

    # get user's month rating
    month_query = user.rating_set.filter(deleted_at__isnull=True, created_at__gte=start_of_month,
                                         created_at__lte=datetime.now()).values('user_id').annotate(rating_month=Sum('rating'))
    if month_query:
        rating_month = int(month_query[0]['rating_month'])
    else:
        rating_month = 0

    return {
        'day': rating_day,
        'day_caption': get_caption(rating_day),
        'week': rating_week,
        'week_caption': get_caption(rating_week),
        'month': rating_month,
        'month_caption': get_caption(rating_month),
    }


def get_caption(value):
    # wraps big numbers in shorter format
    if value >= 1000000:
        return '{0:.1f}m'.format(value/1000000)
    elif value >= 1000:
        return '{0:.1f}k'.format(value/1000)
    else:
        return value


def active_contest_entries(user):
    contest_entries = user.contestsusers_set.filter(
        status='participant', deleted_at__isnull=True).order_by('-id').filter(contest__end_date__gte=datetime.now(), contest__start_date__lte=datetime.now())
    contest_entry = contest_entries.first()
    return contest_entry.contest.slug if contest_entry else contest_entry


def is_chin_chined(user, cuid):

    key = f'user-.{user.id}.-chined-by-.{cuid}'
    if cache.has_key(key):
        is_chined = cache.get(key)
    else:
        chin = ChinChins.objects.filter(
            sender_id=cuid, receiver_id=user.id, created_at__gte=datetime.now()-timedelta(hours=1)).first()
        if chin:
            is_chined = True
            timeout = (chin.created_at + timedelta(hours=1)).total_seconds()
        else:
            is_chined = False
            timeout = (tomorrow() - datetime.now()).total_seconds()
        cache.set(key, is_chined, int(timeout))
    return is_chined


def get_is_active_story(user, cuid, only_active=True, hide_reported=True):

    model = user.storyposts_set.filter(created_at__lte=datetime.now())

    if only_active:
        model = model.filter(created_at__gte=(datetime.now() -
                                              timedelta(days=1)), publish=True).order_by('created_at')
    else:
        model = model.order_by('-created_at')

    if hide_reported:
        reported_posts = ReportedPosts.objects.filter(
            user_id=cuid).values('post_id')
        model = model.filter(~Q(post_id__in=[
            rpost['post_id'] for rpost in reported_posts]) & Q(post__active=True))
    else:
        model = model.order_by('-created_at')

    return model.count()


def is_story_seen(user, cuid):

    query = user.storyposts_set.filter(created_at__range=(datetime.now(), datetime.now(
    )-timedelta(days=1))).filter(post__deleted_at__isnull=True).values('post_id')
    story_post_seen = user.postviews_set.filter(
        post_id__in=[q['post_id'] for q in query]).count()

    story_post_seen = PostViews.objects.filter(
        post_id__in=[q['post_id'] for q in query], user_id=cuid).count()

    return story_post_seen


def follow(user):

    i_follow = user.first.filter(
        deleted_at__isnull=True, accepted_at__isnull=False, second__status__istartswith='active').order_by('-accepted_at')

    return i_follow.count()


def is_subscribed(user, cuid):

    return user.first.filter(first_id=cuid, second_id=user.id, accepted_at__isnull=False).exists()


def followers(user):

    follow_me = user.friends_set.filter(
        deleted_at__isnull=True, accepted_at__isnull=False, first__status__istartswith='active').order_by('-accepted_at')

    return follow_me.count()


def subscribe_requests(user):

    sub_requests = user.friends_set.filter(
        deleted_at__isnull=True, accepted_at__isnull=True, first__status__istartswith='active').order_by('-created_at')

    return sub_requests.count()


def bookmarked_posts(user):
    return user.bookmarks_set.filter(deleted_at__isnull=True).order_by('-updated_at').count()


def mentioned_images(user):
    return user.mentions_set.all().count()


def get_location(additional_info):

    if additional_info and additional_info.lat and additional_info.lng:
        return {
            'lat': additional_info.lat,
            'lng': additional_info.lng
        }
    else:
        return None


def get_timestamp_from_date(dateobj):
    return int(datetime.strptime(str(dateobj), '%Y-%m-%d').strftime("%s"))


def active_gift(user):

    key = f'active-gift-.{user.id}'
    gift_attr = cache.get(key)

    if gift_attr:
        activegift = Gifts.objects.create()
        activegift.id = gift_attr['id']
        activegift.name = gift_attr['name']
        activegift.image = gift_attr['image']
    else:
        activegift = None
    return activegift


def get_gift_resource(user):
    gift = active_gift(user)
    if not gift:
        return None
    else:
        return {
            "id": gift.id,
            "name": gift.name,
            "image": gift.image2 if gift.image2 else gift.image,
        }


def get_background_image_resource(user, is_bg_set_by_gift=False):

    try:
        active_gift_instance = user.giftuser_set.filter(
            accepted_at__isnull=False, expire_at__gte=datetime.now()).order_by('accepted_at').first()
    except GiftUser.DoesNotExist:
        return None
    else:
        gift_user = active_gift_instance
        if gift_user and gift_user.bg_enabled:
            image = gift_user.gift.profile_bg_image
        else:
            image = user.background_image
        if not image:
            return None
        else:
            return {
                'image_id': image.id,
                'bg_origin': image.url,
                'bg_video': image.url_origin,
                'bg_mobile': image.url_medium if image.url_medium else image.url,
                'bg_desk': image.url_large if image.url_large else image.url,
                'bg_static': image.url_small if image.url_small else image.url,
                'is_custom_bg': not is_bg_set_by_gift,
            }


def gift_bg_available(user):

    gift = active_gift(user)
    if not gift:
        return None
    else:
        return gift.profile_bg_image


def get_temp_status_resourse(user):

    try:
        temp_status = user.tempstatuses
    except TempStatuses.DoesNotExist:
        return None
    else:
        if temp_status.already_reset:
            return None
        else:
            return {
                'id': temp_status.id,
                'user_id': temp_status.user_id,
                'expire_at_ts': temp_status.expire_at.strftime("%s"),
                'temp_status_id': temp_status.temp_status_id,
                'reset_status_id': temp_status.reset_status_id,
                'created_at_ts': temp_status.created_at.strftime("%s"),
            }


def get_social_statuses(user):

    social_statuses = SocialStatusDictionary.objects.filter(
        socialstatusbindings__entity_id=user.id).values('id', 'name')

    return list(social_statuses)


def get_activity_statuses(user):

    activity_statuses = FieldOfActivityDictionary.objects.filter(
        fieldofactivitybindings__entity_id=user.id).values('id', 'name')

    return list(activity_statuses)


def get_rating(user):

    rating = get_tabled_rating_sum(user)
    return get_rating_details(rating)


def get_rating_details(current_rating):

    level = get_user_level(current_rating)
    if level > 3:
        level = 3
    if current_rating > 0:
        percent = sqrt(current_rating - ((const.levels[level - 1])
                                         if level > 1 else 0)) * const.ratingCoefficients[level]
    else:
        percent = 0
    percent = percent / 100

    return {
        'level': level,
        'value': int(current_rating),
        'caption': get_caption(current_rating),
        'proportion': round(percent, 4)
    }


def get_user_level(current_rating):
    level = 4
    for lvl, levelrating in const.levels.items():
        if int(current_rating/levelrating) <= 1:
            level = lvl
            return level
    return level


def get_tabled_rating_sum(user):

    key = f'rating.{user.id}'
    if cache.has_key(key):
        rating = cache.get(key)
    else:
        tabled_rating = user.rating_set.filter(
            created_at__lte=datetime.now()).aggregate(Sum('rating'))
        rating = int(tabled_rating['rating__sum'])
        timeout = (tomorrow() - datetime.now()).total_seconds()
        cache.set(key, rating, int(timeout))
    return rating


def tomorrow():
    tomorrow = date.today() + timedelta(days=1)
    return datetime(tomorrow.year, tomorrow.month, tomorrow.day)


def count_offers(user):
    return Offers.objects.filter(post__author_id=user.id).latest('created_at').count()


def is_online(user):
    key = f'UserOnline-{user.id}'
    if not cache.get(key):
        return False
    # key f'UserOnline-{user.id}' is not consistent with key 'online'
    return cache.get('online')


def get_parsed_address_components(place_result, keys={}):
    components = {}
    for a_component in place_result['address_components']:
        for type in a_component['types']:
            components[type] = a_component['long_name']
    return components.keys() & {value: key for key, value in keys.items()} if len(keys) else components


def get_location_google(place_id, lang):

    params = {'place_id': place_id, 'language': lang,
              'key': GOOGLE_PLACES_API_KEY}
    response = requests.get(GOOGLE_API_PLACE_DETAILS_URL,
                            params=params, timeout=10.0)

    if response.status_code == 200:
        return (response.json(), response.status_code)
    else:
        return (f'Unexpected response from {GOOGLE_API_PLACE_DETAILS_URL}', response.status_code)


def get_address_components(place_id, lang='uk'):

    place_details, status_code = get_location_google(place_id, lang)
    if status_code == 200:
        get_parsed_address_components(place_details['result'])

        return get_parsed_address_components(place_details['result'])
    else:
        return None


def add_personal_info(user, user_settings):

    return {
        "email": user.email,
        "phone": user.phone,
        "bookmarks_count": bookmarked_posts(user),
        "mentions_count": mentioned_images(user),
        "settings": {
            "lang": user_settings.lang,
            "chat_langs": {
                "main_lang": user_settings.chat_main_lang,
                "sub_langs": user_settings.chat_sub_langs,
            },
            "chat_autotranslate": user_settings.chat_autotranslate,
            "sounds": user_settings.sounds if user_settings.sounds else True
        },
        "tutorial": {
            "user_id": user.usertutorial.user_id,
            "web_mobile": user.usertutorial.web_mobile,
            "web_desktop": user.usertutorial.web_desktop,
            "android": user.usertutorial.android,
            "ios": user.usertutorial.ios
        },
        "subscribe_requests_count": subscribe_requests(user),
        "gift_bg_available": gift_bg_available(user),
    }
