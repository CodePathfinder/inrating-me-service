from rest_framework import serializers
from .models import Images


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['id', 'url', 'url_large', 'url_medium', 'url_small',
                  'url_origin', 'url_large_origin', 'url_medium_origin', 'url_small_origin']
