from .models import Images, Places, UserPrivacySettings, CommercialButtons, ChinChins, ReportedPosts, PostViews
from . import const
from .serializers import ImagesSerializer
from django.core.cache import cache
from datetime import datetime, date, timedelta
from django.db.models import Sum, Q


def get_response_data(user):

    user_settings = user.usersettings
    additional_info = user.useradditionalinfo
    tutorial = user.usertutorial
    avatar_image = get_avatar_image_resource(user)
    is_commercial = user.parent_id != None
    active_ads_count = user.ads_set.filter(active=True).count()

    """ uncomment to see all cached keys """
    # for k in cache.keys('*'):
    #     print(k)

    main_resource = {
        "id": user.id,
        "nickname": user.nickname,
        # "active_gift": active_gift(user),
        "avatar_image": avatar_image,
        "is_commercial": is_commercial,
        "off_page": user.id == const.inratingAccountID,
        "name": user.name if user.name else user.nickname,
        "lastname": user.lastname if user.lastname else "",
        "status": user.status,
        # "is_subscribed": false,
        # "is_online": false,
        # # "rating": {
        # #     "level": 1,
        # #     "value": 1,
        # #     "caption": 1,
        # #     "proportion": 0.0141
        # # },
        "comments": user_settings.comments if user_settings.comments else "all",
        "geo_id": get_place_resource(user_settings) if user_settings and user_settings.geo_id else 'null',
        "contest_entry_instance": get_contest_resource(user),
        "chat_main_lang": user_settings.chat_main_lang if user_settings.chat_main_lang else 'ru',
        "is_voted": is_voted(user),
        "is_commercial": is_commercial,
        "email": user.email,
        "phone": user.phone,
        "active_ads_count": active_ads_count if active_ads_count else 0,
        "gender": user.gender,

        "background_image": user.background_image_id,
        "birth_date": str(user.birth_date) if user.birth_date else user.birth_date,
        "birth_date_timestamp": get_dob_timestamp(user) if user.birth_date else user.birth_date,
        "typed_rating": get_typed_rating(user),
        "personal_status": user_settings.personal_status,
        "family_status": user_settings.family_status,
        "social_links": user_settings.social_links if user_settings.social_links else [],
        "contest_entry": active_contest_entries(user),
        "is_verified": additional_info.phone_verified if additional_info.phone_verified else False,
        "is_chined": is_chin_chined(user),
        "is_active_story": True if is_active_story(user) else False,
        "is_story_seen": is_story_seen(user) == is_active_story(user),
        # todo id or pk is requered to be added to the model
        # "social_statuses": [{status.id, status.item} for status in user.socialstatusbindings_set.all()],
        # todo id or pk is requered to be added to the model
        # "activity_statuses": [{status.id, status.item} for status in user.fieldofactivitybindings_set.all()],
        # # "offers_count": 0,
        # todo check if 'user.id = author_id' creterium should apply
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
        # # "gift_bg_available": false,
        "location": get_location(additional_info),
        # # "temp_status": null,
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
            cache.set(key, avatar_image)

    return avatar_image


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
        return 'null'


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
        return contest_user


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
            "type": type if type else 'null',
            "value": value if value else 'null'
        }
    except CommercialButtons.DoesNotExist:
        return 'null'


def get_commercial_info(user):

    return {
        "site": user.commercialinfo.site if user.commercialinfo.site else 'null',
        "desc": user.commercialinfo.desc if user.commercialinfo.desc else 'null',
        "categories": get_categories(user) if get_categories(user) else 'null',
        "button": get_commercial_button_resource(user),
    }


def get_typed_rating(user):
    """ Get user's rating data from cache, if not available - retrieve from DB """
    key = f'typed-rating-.{user.id}'
    if cache.has_key(key):
        rating = cache.get(key)
    else:
        rating = typed_rating(user)
        tmrw = date.today() + timedelta(days=1)
        timeout = (datetime(tmrw.year, tmrw.month, tmrw.day) -
                   datetime.now()).total_seconds()
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
    day_query = user.rating_set.filter(deleted_at__isnull=True, created_at__gte=today,
                                       created_at__lte=datetime.now()).values('user_id').annotate(rating_day=Sum('rating'))
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


def get_caption(number):
    """ Wraps big numbers in short format """
    if number >= 1000000:
        return '{0:.1f}m'.format(number/1000000),
    elif number >= 1000:
        return '{0:.1f}k'.format(number/1000),
    else:
        return number


def active_contest_entries(user):
    contest_entries = user.contestsusers_set.filter(
        status='participant', deleted_at__isnull=True).order_by('-id').filter(contest__end_date__gte=datetime.now(), contest__start_date__lte=datetime.now())
    contest_entry = contest_entries.first()
    return contest_entry.contest.slug if contest_entry else contest_entry


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
            tomorrow = date.today() + timedelta(days=1)
            timeout = (datetime(tomorrow.year, tomorrow.month, tomorrow.day) -
                       datetime.now()).total_seconds()
        cache.set(key, is_chined, int(timeout))
    return is_chined


def is_active_story(user, only_active=True, hide_reported=True):

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
    story_post_seen = PostViews.objects.filter(
        post_id__in=[q['post_id'] for q in query], user_id=user.id).count()

    return story_post_seen


def follow(user):

    i_follow = user.first.filter(
        deleted_at__isnull=True, accepted_at__isnull=False, second__status__istartswith='active').order_by('-accepted_at')

    return i_follow.count()


def followers(user):

    follow_me = user.friends_set.filter(
        deleted_at__isnull=True, accepted_at__isnull=False, first__status__istartswith='active').order_by('-accepted_at')

    return follow_me.count()


def bookmarked_posts(user):
    return user.bookmarks_set.filter(deleted_at__isnull=True).order_by('-updated_at').count()


def mentioned_images(user):
    return user.mentions_set.all().count()


def subscribe_requests(user):

    sub_requests = user.friends_set.filter(
        deleted_at__isnull=True, accepted_at__isnull=True, first__status__istartswith='active').order_by('-created_at')

    return sub_requests.count()


def get_location(additional_info):

    if additional_info and additional_info.lat and additional_info.lng:
        return {
            'lat': additional_info.lat,
            'lng': additional_info.lng
        }
    else:
        return 'null'


def get_dob_timestamp(user):
    return int(datetime.strptime(str(user.birth_date), '%Y-%m-%d').strftime("%s"))


# TODO
def active_gift(user):

    key = f'active-gift-.{user.id}'

    if cache.get(key):
        gift_attr = cache.get(key)
    else:
        gift_attr = True

    if gift_attr:
        # activegift = Gifts.objects.create()
        # activegift.id = gift_attr['id']
        # activegift.name = gift_attr['name']
        # activegift.image = gift_attr['image']
        # activegift.save()
        activegift = True
    else:
        activegift = None

    return activegift
