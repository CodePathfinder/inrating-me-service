from django.db import models


class Users(models.Model):

    nickname = models.CharField(unique=True, max_length=255)
    email = models.CharField(
        max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(
        max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    lastname = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=16, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar_image = models.OneToOneField(
        'Images', on_delete=models.SET_NULL, blank=True, null=True)
    avatar_post_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField()
    coins = models.IntegerField(blank=True, null=True, default=0)
    face_api_gender = models.CharField(max_length=16, blank=True, null=True)
    background_image = models.OneToOneField(
        'Images', on_delete=models.SET_NULL, related_name='bg_image', blank=True, null=True)
    freecoins = models.IntegerField(blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class Ads(models.Model):
    user = models.ForeignKey(Users, on_delete=models.DO_NOTHING)
    post = models.ForeignKey('Posts', on_delete=models.DO_NOTHING)
    result = models.CharField(max_length=191)
    link = models.CharField(max_length=191, blank=True, null=True)
    targeting_type = models.CharField(max_length=191)
    # filter = models.ForeignKey(AdFilters, on_delete=models.CASCADE)
    price = models.FloatField()
    day_actions = models.IntegerField()
    day_budget = models.IntegerField()
    days = models.IntegerField()
    finish = models.DateTimeField()
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    moderated = models.BooleanField(default=False)
    start = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ads'


class Bookmarks(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    post = models.ForeignKey('Posts', on_delete=models.CASCADE)
    # primary_key=True is added to 'created_at' field, as there is no 'id' field
    created_at = models.DateTimeField(primary_key=True)
    deleted_at = models.DateTimeField(blank=True, null=True, default='Null')
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'bookmarks'
        unique_together = (('user', 'post'),)


class ChinChins(models.Model):
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'chin_chins'


class CommercialButtons(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    type = models.CharField(max_length=191, blank=True, null=True)
    value = models.CharField(max_length=191, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'commercial_buttons'


class CommercialCategories(models.Model):
    name = models.CharField(max_length=191)

    class Meta:
        managed = False
        db_table = 'commercial_categories'


class CommercialCategoryUser(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    category = models.ForeignKey(
        CommercialCategories, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'commercial_category_user'


class CommercialInfo(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    site = models.CharField(max_length=191, blank=True, null=True)
    desc = models.CharField(max_length=191, blank=True, null=True)
    extended_channel_statistic = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'commercial_info'


class ContestRating(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    rating = models.FloatField()
    # Field is renamed because of name conflict.
    rating_0 = models.ForeignKey(
        'Rating', on_delete=models.DO_NOTHING, db_column='rating_id')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contest_rating'


class Contests(models.Model):
    name = models.CharField(max_length=255)
    organiser = models.CharField(max_length=255)
    desc = models.TextField()
    img = models.CharField(max_length=255)
    admin_id = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    slug = models.CharField(max_length=255, blank=True, null=True)
    salt = models.CharField(max_length=16, blank=True, null=True)
    max_contestants_count = models.SmallIntegerField(
        blank=True, null=True, default=0)
    deleted_at = models.DateTimeField(blank=True, null=True)
    app_submission_start_date = models.DateTimeField(blank=True, null=True)
    app_submission_end_date = models.DateTimeField(blank=True, null=True)
    extra_field_id = models.IntegerField(blank=True, null=True)
    rating = models.BooleanField(default=False)
    # type = models.ForeignKey(
    #     'ContestTypes', on_delete=models.SET_DEFAULT, db_column='type', default=1)
    desc_short = models.CharField(max_length=255, blank=True, null=True)
    round_to = models.CharField(max_length=20, blank=True, null=True)
    # category = models.ForeignKey(
    #     'ContestCategories', on_delete=models.SET_NULL, blank=True, null=True)
    top_position = models.SmallIntegerField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    # banner_img = models.ForeignKey(
    #     'Banners', on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contests'


class ContestsUsers(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contests, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, default='user')
    current_contest_post = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    contest_admin_id = models.DecimalField(
        max_digits=255, decimal_places=0, blank=True, null=True)
    contest_user_extra = models.CharField(
        max_length=255, blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'contests_users'


class FieldOfActivityDictionary(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'field_of_activity_dictionary'
        unique_together = (('id', 'name'),)


class FieldOfActivityBindings(models.Model):
    item = models.ForeignKey(
        FieldOfActivityDictionary, on_delete=models.CASCADE)
    entity = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'field_of_activity_bindings'
        unique_together = (('item_id', 'entity_id'),)


class Friends(models.Model):

    first = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='first')
    second = models.ForeignKey(Users, on_delete=models.CASCADE)
    created_at = models.DateTimeField(primary_key=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'friends'
        unique_together = (('first', 'second'),)


class GiftUser(models.Model):
    sender = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='sender')
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    gift = models.ForeignKey('Gifts', on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    accepted_at = models.DateTimeField(blank=True, null=True)
    expire_at = models.DateTimeField(blank=True, null=True)
    is_seen = models.BooleanField(default=False)
    updated_at = models.DateTimeField(blank=True, null=True)
    message = models.CharField(max_length=55, blank=True, null=True)
    bg_enabled = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'gift_user'


class Gifts(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    cost = models.IntegerField()
    description = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    bonus = models.TextField()
    properties = models.JSONField(default=dict, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    profile_bg_image = models.OneToOneField(
        'Images', on_delete=models.SET_NULL, blank=True, null=True)
    cost_freecoins = models.IntegerField(null=True, blank=True)
    available = models.BooleanField(default=True)
    icon_bg_image_id = models.CharField(max_length=191, null=True, blank=True)
    image2 = models.CharField(max_length=200, null=True, blank=True)
    days_to_accept = models.SmallIntegerField(default='1')

    class Meta:
        managed = False
        db_table = 'gifts'
        verbose_name_plural = 'Gifts'

    def __str__(self):
        return self.name


class Images(models.Model):

    author_id = models.IntegerField(blank=True, null=True)
    url = models.CharField(max_length=255)
    url_large = models.CharField(max_length=255, blank=True, null=True)
    url_medium = models.CharField(max_length=255, blank=True, null=True)
    url_small = models.CharField(max_length=255, blank=True, null=True)
    server_id = models.SmallIntegerField(default=1)
    url_origin = models.CharField(max_length=255, blank=True, null=True)
    url_large_origin = models.CharField(max_length=255, blank=True, null=True)
    url_medium_origin = models.CharField(max_length=255, blank=True, null=True)
    url_small_origin = models.CharField(max_length=255, blank=True, null=True)
    tag = models.CharField(max_length=64, blank=True, null=True)
    # group = models.ForeignKey(
    #     Groups, on_delete=models.CASCADE, blank=True, null=True)
    url_shape_cropped_round = models.CharField(
        max_length=255, blank=True, null=True)
    url_shape_cropped_star = models.CharField(
        max_length=255, blank=True, null=True)
    url_shape_cropped_diamond = models.CharField(
        max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'images'


class Mentions(models.Model):

    item = models.ForeignKey(Images, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mentions'


class Places(models.Model):

    google_place_id = models.CharField(max_length=255, blank=True, null=True)
    uk = models.CharField(max_length=255, blank=True, null=True)
    ru = models.CharField(max_length=255, blank=True, null=True)
    en = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    locality = models.CharField(max_length=191, blank=True, null=True)
    country = models.CharField(max_length=191, blank=True, null=True)
    administrative_area_level_1 = models.CharField(
        max_length=191, blank=True, null=True)
    administrative_area_level_2 = models.CharField(
        max_length=191, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'places'


class PostViews(models.Model):

    post_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'post_views'
        unique_together = (('post_id', 'user_id'),)


class Posts(models.Model):
    author = models.ForeignKey('Users', on_delete=models.CASCADE)
    title = models.CharField(
        max_length=5000, blank=True, null=True, default='null')
    slug = models.CharField(unique=True, max_length=255)
    type = models.SmallIntegerField()
    active = models.BooleanField(default=True)
    geo_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    body = models.IntegerField(default=0)
    body_type = models.CharField(max_length=5, default='image')
    bookmarkable = models.CharField(
        max_length=20, blank=True, null=True, default='all')
    visibility = models.SmallIntegerField(default=2)
    allow_comments = models.BooleanField(default=True)
    content = models.TextField(blank=True, null=True)
    repost_of = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'posts'


class Rating(models.Model):

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=65535, decimal_places=16383)
    created_at = models.DateTimeField()
    type = models.CharField(max_length=5, blank=True, null=True)
    sender_id = models.IntegerField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rating'


class ReportedPosts(models.Model):
    post_id = models.IntegerField()
    user_id = models.IntegerField()
    created_at = models.DateTimeField()
    status = models.SmallIntegerField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reported_posts'
        unique_together = (('post_id', 'user_id'),)


class SocialStatusDictionary(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'social_status_dictionary'


class SocialStatusBindings(models.Model):
    item = models.ForeignKey(
        SocialStatusDictionary, on_delete=models.CASCADE)
    entity = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'social_status_bindings'
        unique_together = (('item_id', 'entity_id'),)


class StoryPosts(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    created_at = models.DateTimeField(primary_key=True)
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    publish = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'story_posts'
        unique_together = (('user', 'post'),)


class TempStatuses(models.Model):

    user = models.OneToOneField(
        Users, on_delete=models.CASCADE, blank=True, null=True)
    temp_status_id = models.IntegerField()
    expire_at = models.DateTimeField()
    reset_status_id = models.IntegerField()
    already_reset = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'temp_statuses'


class UserAdditionalInfo(models.Model):

    user = models.OneToOneField(
        Users, on_delete=models.CASCADE)
    phone_codes_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    extra_fee_ios_android = models.BooleanField(
        blank=True, null=True, default=False)
    facebook_id = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    phone_verified = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'user_additional_info'


class UserExtrarate(models.Model):
    exchange_id = models.IntegerField(default=0)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    sender_id = models.IntegerField(default=0)
    rate = models.FloatField()
    type = models.IntegerField(default=0)
    updated_at = models.DateTimeField()
    created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_extrarate'


class UserPrivacySettings(models.Model):

    user = models.OneToOneField(
        Users, on_delete=models.CASCADE, primary_key=True)
    profile = models.CharField(max_length=10, default='all')
    subscribers = models.CharField(max_length=10, default='all')
    subscriptions = models.CharField(max_length=10, default='all')
    chat = models.CharField(max_length=10, default='all')
    subscribe = models.CharField(max_length=10, default='all')
    groups = models.CharField(max_length=10, blank=True, null=True)
    posts_home = models.CharField(
        max_length=10, blank=True, null=True, default='all')
    stories = models.CharField(
        max_length=10, blank=True, null=True, default='all')

    class Meta:
        managed = False
        db_table = 'user_privacy_settings'


class UserSettings(models.Model):

    user = models.OneToOneField(
        Users, on_delete=models.CASCADE, primary_key=True)
    lang = models.CharField(max_length=16, blank=True, null=True)
    geo_id = models.IntegerField(blank=True, null=True)
    personal_status = models.CharField(max_length=255, blank=True, null=True)
    family_status = models.CharField(max_length=16, blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)
    sounds = models.CharField(max_length=16, blank=True, null=True)
    comments = models.CharField(max_length=10, blank=True, null=True)
    chat_main_lang = models.CharField(max_length=3, blank=True, null=True)
    chat_sub_langs = models.JSONField(blank=True, null=True)
    chat_autotranslate = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'user_settings'


class UserTutorial(models.Model):
    user = models.OneToOneField(
        Users, on_delete=models.CASCADE, primary_key=True)
    web_mobile = models.BooleanField(default=False)
    web_desktop = models.BooleanField(default=False)
    android = models.BooleanField(default=False)
    ios = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'user_tutorial'


class Offers(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.DO_NOTHING)
    reach_from = models.IntegerField(blank=True, null=True)
    reach_to = models.IntegerField(blank=True, null=True)
    age_from = models.IntegerField(blank=True, null=True)
    age_to = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=191, blank=True, null=True)
    place = models.ForeignKey(Places, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exchange.offers'
