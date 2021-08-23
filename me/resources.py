from datetime import datetime, date, timedelta
from django.db.models import Sum, Q
from django.core.cache import cache
from django.utils.translation import ugettext as _
from math import sqrt

from .models import Images, Places, UserPrivacySettings, CommercialButtons, ChinChins, ReportedPosts, GiftUser, Gifts, TempStatuses, FieldOfActivityDictionary, SocialStatusDictionary
from .serializers import ImagesSerializer
from . import const


def get_response_data(user):

    user_settings = user.usersettings
    additional_info = user.useradditionalinfo
    tutorial = user.usertutorial
    avatar_image = get_avatar_image_resource(user)
    is_commercial = user.parent_id != None
    active_ads_count = user.ads_set.filter(active=True).count()
    is_active_story = get_is_active_story(user)
    contest_resource = get_contest_resource(user)

    """ uncomment to see all cached keys """
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
        "is_subscribed": is_subscribed(user),
        # "is_online": false,
        "rating": get_rating(user),
        "comments": user_settings.comments if user_settings.comments else "all",
        "geo_id": get_place_resource(user_settings) if user_settings and user_settings.geo_id else None,
        "contest_entry_instance": contest_resource,
        "chat_main_lang": user_settings.chat_main_lang if user_settings.chat_main_lang else 'ru',
        "is_voted": is_voted(user),
        "is_commercial": is_commercial,
        "email": user.email,
        "phone": user.phone,
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
        "is_chined": is_chin_chined(user),
        "is_active_story": True if is_active_story else False,
        "is_story_seen": is_story_seen(user) == is_active_story,
        "social_statuses": get_social_statuses(user),
        "activity_statuses": get_activity_statuses(user),
        # # "offers_count": 0,
        "posts_count": user.posts_set.filter(type=const.postTypes['user-post'], deleted_at__isnull=True).count(),
        "subscriptions_count": follow(user),
        "subscribers_count": followers(user),
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
            "user_id": tutorial.user_id,
            "web_mobile": tutorial.web_mobile,
            "web_desktop": tutorial.web_desktop,
            "android": tutorial.android,
            "ios": tutorial.ios
        },
        "subscribe_requests_count": subscribe_requests(user),
        "gift_bg_available": gift_bg_available(user),
        "location": get_location(additional_info),
        "temp_status": get_temp_status_resourse(user),
        "privacy_settings": get_user_privacy_settings_resource(user)
    }
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
            # avatar_image['mentioned_users_count'] = mentioned_users(user)
            cache.set(key, avatar_image)

    return avatar_image

# TODO
# def mentioned_users(user):
#     try:
#         mentioned_users =
#         return mentioned_users.count()
#     except Object.DoesNotExist:
#         return 0


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


def get_location_place_resource(lang, place):
    """ get location colomn (uk, ru, or en) depending on user's main language """

    if lang == const.locationLanguages['uk']:
        location = place.uk
    elif lang == const.locationLanguages['ru']:
        location = place.ru
    elif lang == const.locationLanguages['en']:
        location = place.en
    else:
        location = place.en
    return location


def get_place_resource(user_settings):
    try:
        place = Places.objects.get(id=user_settings.geo_id)
        place_resource = {
            "id": place.id,
            "google_place_id": place.google_place_id,
            "location": get_location_place_resource(user_settings.lang, place),
            "lat": place.lat,
            "lng": place.lng,
            "locality": place.locality,
            "country": place.country,
            "administrative_area_level_1": place.administrative_area_level_1,
            "administrative_area_level_2": place.administrative_area_level_2,
            # "address_components": [?]
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


def is_voted(user):

    key = f'user-.{user.id}.-voted-by-.{user.id}'
    if cache.has_key(key):
        is_voted = cache.get(key)
    else:
        votes = user.userextrarate_set.filter(sender_id=user.id, type=1).filter(
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
        "site": user.commercialinfo.site if user.commercialinfo.site else None,
        "desc": user.commercialinfo.desc if user.commercialinfo.desc else None,
        "categories": get_categories(user) if get_categories(user) else None,
        "button": get_commercial_button_resource(user),
    }


def get_typed_rating(user):
    """ Get user's rating data from cache, if not available - retrieve from DB """
    key = f'typed-rating-.{user.id}'
    if cache.has_key(key):
        rating = cache.get(key)
    else:
        rating = typed_rating(user)
        timeout = (tomorrow() - datetime.now()).total_seconds()
        cache.set(key, rating, int(timeout))
    return rating


def typed_rating(user):
    """ Retrive user's rating data from DB """
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
    """ Wraps big numbers in short format """
    if value >= 1000000:
        return '{0:.1f}m'.format(value/1000000),
    elif value >= 1000:
        return '{0:.1f}k'.format(value/1000),
    else:
        return value


def is_chin_chined(user):

    key = f'user-.{user.id}.-chined-by-.{user.id}'
    if cache.has_key(key):
        is_chined = cache.get(key)
    else:
        chin = ChinChins.objects.filter(
            sender_id=user.id, receiver_id=user.id, created_at__gte=datetime.now()-timedelta(hours=1)).first()
        if chin:
            is_chined = True
            timeout = (chin.created_at + timedelta(hours=1)).total_seconds()
        else:
            is_chined = False
            timeout = (tomorrow() - datetime.now()).total_seconds()
        cache.set(key, is_chined, int(timeout))
    return is_chined


def get_is_active_story(user, only_active=True, hide_reported=True):

    model = user.storyposts_set.filter(created_at__lte=datetime.now())

    if only_active:
        model = model.filter(created_at__gte=(datetime.now() -
                                              timedelta(days=1)), publish=True).order_by('created_at')
    else:
        model = model.order_by('-created_at')

    if hide_reported:
        reported_posts = ReportedPosts.objects.filter(
            user_id=user.id).values('post_id')
        model = model.filter(~Q(post_id__in=[
            rpost['post_id'] for rpost in reported_posts]) & Q(post__active=True))
    else:
        model = model.order_by('-created_at')

    return model.count()


def is_story_seen(user):

    query = user.storyposts_set.filter(created_at__range=(datetime.now(), datetime.now(
    )-timedelta(days=1))).filter(post__deleted_at__isnull=True).values('post_id')
    story_post_seen = user.postviews_set.filter(
        post_id__in=[q['post_id'] for q in query]).count()

    return story_post_seen


def follow(user):

    i_follow = user.first.filter(
        deleted_at__isnull=True, accepted_at__isnull=False, second__status__istartswith='active').order_by('-accepted_at')

    return i_follow.count()


def is_subscribed(user):

    return user.first.filter(first_id=user.id, second_id=user.id, accepted_at__isnull=False).exists()


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
            "name": _(gift.name),
            # "name" => __( 'gifts.gift_title_' . $this->id ), Localization
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

    # level = get_user_level(current_rating)
    # if level > 3:
    #     level = 3
    # if current_rating > 0:
    #     # TODO: clarify what is 'self::levels' and 'self::ratingCoefficients'
    #     percent = sqrt(current_rating - ((self: : levels[level - 1]) if level > 1 else 0)) * self: : ratingCoefficients[level]
    # else:
    #     percent = 0
    # percent = percent / 100
    return {
        # 'level': level,
        'value': int(current_rating),
        'caption': get_caption(current_rating),
        # 'proportion': round(percent, 4)
    }


def get_user_level(current_rating):
    level = 4
    # TODO: clarify what is 'self::levels'
    for lev in levels:
        if int(current_rating/lev['levelrating']) <= 1:
            level = lev['level']
            break
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
