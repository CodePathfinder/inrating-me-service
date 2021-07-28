from django.db import models
import calendar
from datetime import datetime


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
    avatar_image_id = models.IntegerField(blank=True, null=True)
    avatar_post_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField()
    coins = models.IntegerField(blank=True, null=True, default=0)
    face_api_gender = models.CharField(max_length=16, blank=True, null=True)
    background_image_id = models.BigIntegerField(blank=True, null=True)
    freecoins = models.IntegerField(blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'

    @property
    def get_dob_timestamp(self):
        return int(datetime.strptime(str(self.birth_date), '%Y-%m-%d').strftime("%s"))

    # @property
    # def get_dob_timestamp(self):
    #     d = self.birth_date
    #     dt = datetime(d.year, d.month, d.day)
    #     timetuple = datetime.utctimetuple(dt)
    #     return calendar.timegm(timetuple)


class UserSettings(models.Model):

    user_id = models.IntegerField(primary_key=True)
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


class Groups(models.Model):

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10)
    subject = models.SmallIntegerField(blank=True, null=True)
    description = models.CharField(max_length=5000)
    slug = models.CharField(max_length=100)
    accessibility = models.CharField(max_length=10)
    logo = models.IntegerField(blank=True, null=True)
    banner = models.IntegerField(blank=True, null=True)
    website = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    geo_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    fee = models.SmallIntegerField(blank=True, null=True)
    coins = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'groups'


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
    group = models.ForeignKey(
        'Groups', on_delete=models.CASCADE, blank=True, null=True)
    url_shape_cropped_round = models.CharField(
        max_length=255, blank=True, null=True)
    url_shape_cropped_star = models.CharField(
        max_length=255, blank=True, null=True)
    url_shape_cropped_diamond = models.CharField(
        max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'images'


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


class AdFilters(models.Model):

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    locs = models.TextField(blank=True, null=True)
    age = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=191, blank=True, null=True)
    social_statuses = models.TextField(blank=True, null=True)
    activity_statuses = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ad_filters'


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


class UserPrivacySettings(models.Model):
    user_id = models.IntegerField(primary_key=True)
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


class Gifts(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    cost = models.IntegerField()
    description = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    bonus = models.TextField()
    properties = models.JSONField(default=dict, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    profile_bg_image_id = models.BigIntegerField(null=True, blank=True)
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

    """ Serialize method converts object of dict and adjusts key-value pairs """

    def serialize(self):

        return {
            "id": self.id,
            "name": self.name,
            "cost": self.cost,
            "description": self.description,
            "image": self.image,
            "bonus": self.bonus,
            "properties": self.properties,
            "status": self.status,
            "profile_bg_image_id": self.profile_bg_image_id,
            "cost_freecoins": self.cost_freecoins,
            "available": self.available,
            "icon_bg_image_id": self.icon_bg_image_id,
            "image2": self.image2,
            "days_to_accept": self.days_to_accept
        }
