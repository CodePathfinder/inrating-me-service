from django.shortcuts import HttpResponse, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64

from . models import Gifts
from . utils import timestamp_token_verification


def index(request):
    return render(request, 'api_gifts/index.html')


@csrf_exempt
def gifts(request):
    """ in response to url request: v1/gifts/available/, gets lists of objects with different status field
        and returns JSON in required pattern {"FREE":[], "GOLD":[], "PLATINUM":[], "Premium":[], "VIP:[]"} """

    if request.method == 'POST':

        gifts = Gifts.objects.filter(available=True).order_by('id')
        # print(len(gifts))
        response_data = {}
        STATUSLIST = ['FREE', 'GOLD', 'PLATINUM', 'Premium', 'VIP']

        for status in STATUSLIST:
            response_data[status] = [
                gift.serialize() for gift in gifts.filter(status__icontains=status)
            ]

        return HttpResponse(json.dumps(response_data, ensure_ascii=False), content_type="application/json")

    return JsonResponse({'Error': 'POST request required.'}, status=400)


@csrf_exempt
def me_info(request):

    if request.method == 'POST':

        # caseinsensitive check if 'Authorization' key in request.headers dict
        if 'Authorization' in request.headers and request.headers['Authorization']:

            try:
                # get value of 'Authorization' key and get rid of 'Bearer ' substring
                token = (request.headers['Authorization']).split(' ')[1]

                # split token string by (.) and extract encripted payload data
                token_data = token.split('.')[1]

            except IndexError:
                return JsonResponse(
                    {'Error': "Invalid token format."}, status=400)

            # decode payload data(b64decode), convert binary into string(decode), and convert JSON string to dictionary(json.loads)
            try:
                data = json.loads(base64.b64decode(token_data + '=='))

            except json.decoder.JSONDecodeError:
                return JsonResponse(
                    {'Error': "Invalid authorisation token. JSONDecodeError"}, status=400)

            """ Token verification and authorization block"""

            # 1) verify token integrity, if practicable
            # SECRET OR PUBLIC KEY REQUIRED

            # 2) verify if the token is not expired

            if not timestamp_token_verification(data):
                return JsonResponse(
                    {'Error': "Authorisation token is invalid or expired."}, status=400)

            # 3) verify validity of token id, if practicable
            # AVAILABLE BY QUERY TO DB

            # 4) verify scope of user's rights(authrization), if practicable

            """ End token verification and authorization block """

            # extract 'sub(ject)'/'user_id' from payload data
            if 'sub' in data:
                id = int(data['sub'])

                # TODO: query to table user and related tables in DB and add 'me' dict

                response_data = {'id': id}

                return JsonResponse(response_data)
            else:
                return JsonResponse(
                    {'Error': "Invalid authorisation token."}, status=400)

        else:
            return JsonResponse({'Error': "No Authorisation token."}, status=400)

    else:
        return JsonResponse({'Error': 'POST request required.'}, status=400)
