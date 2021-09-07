from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.cache import cache_page

import json
import base64
import time

from .models import Users
from .resources import get_response_data


def index(request):
    return HttpResponse('<h2>TEST CONNECTION</h2>')


@api_view(['GET', 'POST'])
@cache_page(60 * 5)
def me_info(request):

    if request.method == 'POST':

        # check if 'Authorization' key in request.headers dict
        if 'Authorization' in request.headers and request.headers['Authorization']:

            try:
                # get value of 'Authorization' key and get rid of 'Bearer ' substring
                token = (request.headers['Authorization']).split(' ')[1]

                # split token string by (.) and extract encripted payload data
                token_data = token.split('.')[1]

            except IndexError:
                return Response(
                    {'Error': "Invalid token format."}, status=status.HTTP_400_BAD_REQUEST)

            # decode payload data(b64decode) and convert JSON string to dictionary(json.loads)
            try:
                data = json.loads(base64.b64decode(token_data + '=='))

            except json.decoder.JSONDecodeError:
                return Response(
                    {'Error': "Invalid authorisation token. JSONDecodeError"}, status=status.HTTP_400_BAD_REQUEST)

            if not timestamp_token_verification(data):
                return Response(
                    {'Error': "Authorisation token is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)

            # extract 'sub(ject)'/'user_id' from payload data
            if 'sub' in data:
                id = int(data['sub'])

                # check if user's id is in DB and is unique, get 'me'- related data from DB (users)
                try:
                    me = Users.objects.select_related('avatar_image', 'background_image', 'commercialbuttons', 'commercialinfo',
                                                      'tempstatuses', 'useradditionalinfo', 'userprivacysettings', 'usersettings', 'usertutorial').get(id=id)
                except Users.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                # JSON representation of DB data
                response_data = get_response_data(me)

                return Response(response_data)

            else:
                return Response(
                    {'Error': "Invalid Authorisation token."}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'Error': "No Authorisation token."}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'Error': 'POST request required.'}, status=status.HTTP_400_BAD_REQUEST)


def timestamp_token_verification(data):
    # check if authorization token is not expired

    try:
        iat = data.get('iat')
        exp = data.get('exp')
    except Exception:
        return False
    else:
        now = int(time.time())
        if iat >= now or exp <= now:
            return False
        else:
            return True
