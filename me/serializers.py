from rest_framework import serializers
from .models import Images


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = [
            'id', 'author_id', 'url', 'url_large', 'url_medium',
            'url_small', 'server_id', 'url_origin', 'url_large_origin', 'url_medium_origin', 'url_small_origin', 'tag', 'group', 'url_shape_cropped_round', 'url_shape_cropped_star', 'url_shape_cropped_diamond'
        ]
