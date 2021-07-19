from django.db import models

# Create your models here.


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
