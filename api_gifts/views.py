from django.shortcuts import HttpResponse, render
from django.http import JsonResponse
from django.utils.encoding import force_text, smart_str
from django.db import connection
import json


def index(request):
    return HttpResponse('<h1>Here may be a page from which JSON data are requested from the server and where response data may be displayed (with some JS code)<\h1>')


def gifts(request):
    
    """ in response to url request: v1/gifts/available/, gets lists of objects with different status field 
        and returns JSON in required pattern {"FREE":[], "GOLD":[], "PLATINUM":[], "Premium":[]} """

    gifts_free = dictfetchall('FREE')
    gifts_gold = dictfetchall('GOLD')
    gifts_platinum = dictfetchall('PLATINUM')
    gifts_premium = dictfetchall('Premium')
    
    response_data = {"FREE":gifts_free, "GOLD":gifts_gold, "PLATINUM":gifts_platinum, "Premium":gifts_premium}
    
    return HttpResponse(json.dumps(response_data, ensure_ascii=False), content_type="application/json")


def dictfetchall(status):
    
    """ Makes raw queries to DB and returns all rows from a cursor as a list of dict 
        with key-value pairs as set in serialize function """

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM gifts WHERE status = '%s' LIMIT 1" % status)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return [serialize(row) for row in rows]
      

def serialize(row):

    """ Allows to configure object/dict (for instance, set/rename keys 
        or comment/delete unnecessary key-value pairs """

    print(row['name'])
    print(type(row['name']))
    return {
        "id": row['id'],
        "name": row['name'],
        "cost": row['cost'],
        "description": row['description'],
        "image": row['image'],
        "bonus": row['bonus'],
        "properties": row['properties'],
        "status": row['status'],
        "profile_bg_image_id": row['profile_bg_image_id'],
        "cost_freecoins": row['cost_freecoins'],
        "available": row['available'],
        "icon_bg_image_id": row['icon_bg_image_id'],
        "image2": row['image2'],
        "days_to_accept": row['days_to_accept']
    }
