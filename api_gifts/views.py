from django.shortcuts import HttpResponse, render
from django.http import JsonResponse
# from django.db import connection
from . models import Gifts
import json


def index(request):
    return render(request, 'api_gifts/index.html')


def gifts(request):
    """ in response to url request: v1/gifts/available/, gets lists of objects with different status field
        and returns JSON in required pattern {"FREE":[], "GOLD":[], "PLATINUM":[], "Premium":[], "VIP:[]"} """

    if request.method == 'POST':

        gifts = Gifts.objects.all().values().order_by('id')
        response_data = {}
        STATUSLIST = ['FREE', 'GOLD', 'PLATINUM', 'Premium', 'VIP']

        for status in STATUSLIST:
            response_data[status] = [
                serialize(gift) for gift in list(gifts.filter(status__icontains=status))
            ]

        return HttpResponse(json.dumps(response_data, ensure_ascii=False), content_type="application/json")

    return JsonResponse({'Error': 'POST request required.'}, status=400)


def serialize(gift):
    """ Allows to configure object/dict (for instance, set/rename keys
        or comment/delete unnecessary key-value pairs """

    return {
        "id": gift['id'],
        "name": gift['name'],
        "cost": gift['cost'],
        "description": gift['description'],
        "image": gift['image'],
        "bonus": gift['bonus'],
        "properties": gift['properties'],
        "status": gift['status'],
        "profile_bg_image_id": gift['profile_bg_image_id'],
        "cost_freecoins": gift['cost_freecoins'],
        "available": gift['available'],
        "icon_bg_image_id": gift['icon_bg_image_id'],
        "image2": gift['image2'],
        "days_to_accept": gift['days_to_accept']
    }
