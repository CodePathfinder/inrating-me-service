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
    # created_at 'timestamp(0) without time zone NOT NULL DEFAULT now()' in orginal - possible default values: auto_now_add=True or default=timezone.now - from django.utils.timezone.now()
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


class Gifts(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    cost = models.IntegerField()
    description = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    bonus = models.TextField()
    properties = models.JSONField(default='{}', null=True, blank=True)
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
