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
def get_user_data(request):

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

            # extract 'current user id' (cuid) from payload data
            if 'sub' in data:
                cuid = int(data['sub'])

                message = ''

                # get request.data containing either request.body (json) or request.POST (form) data
                try:
                    body = request.data
                except Exception:
                    return Response(
                        {'Error': 'Usage: "nickname": "< string >", "id": "< integer >".'}, status=status.HTTP_400_BAD_REQUEST)

                # if 'nickname' in request.data, validate 'nickname', try and extract user data by 'nickname'
                if 'nickname' in body:
                    if body["nickname"]:
                        if not isinstance(body["nickname"], str):
                            return Response(
                                {'ValidationError': "nickname should be a string."}, status=status.HTTP_400_BAD_REQUEST)
                        if len(body["nickname"]) > 255:
                            return Response(
                                {'ValidationError': "max lenght of nickname should be 255."}, status=status.HTTP_400_BAD_REQUEST)
                        nickname = body["nickname"]
                        print("nickname: ", nickname)
                        if Users.objects.filter(nickname=nickname).exists():
                            user = Users.objects.select_related('avatar_image', 'background_image', 'commercialbuttons', 'commercialinfo',
                                                                'tempstatuses', 'useradditionalinfo', 'userprivacysettings', 'usersettings', 'usertutorial').get(nickname=nickname)
                            return Response(get_response_data(user, cuid))
                        else:
                            message = f'No user is found with nickname: {nickname}.'
                    else:
                        message = 'No value is provided for nickname.'

                # if 'id' in request.data, try and extract user data by 'id'
                if 'id' in body:
                    if body["id"]:
                        try:
                            id = int(body["id"])
                        except ValueError:
                            return Response(
                                {'ValidationError': "id should be an integer."}, status=status.HTTP_400_BAD_REQUEST)

                        try:
                            user = Users.objects.select_related('avatar_image', 'background_image', 'commercialbuttons', 'commercialinfo',
                                                                'tempstatuses', 'useradditionalinfo', 'userprivacysettings', 'usersettings', 'usertutorial').get(id=id)
                            return Response(get_response_data(user, cuid))
                        except Users.DoesNotExist:
                            message += f'No user is found with id: {id}.'
                            return Response({'NOT FOUND': message}, status=status.HTTP_404_NOT_FOUND)
                    else:
                        message += 'No value is provided for id.'
                if message:
                    return Response({'Error': message}, status=status.HTTP_400_BAD_REQUEST)

                # extract user data by 'current user id' if neither nickname nor id is provided in request.data
                try:
                    user = Users.objects.select_related('avatar_image', 'background_image', 'commercialbuttons', 'commercialinfo',
                                                        'tempstatuses', 'useradditionalinfo', 'userprivacysettings', 'usersettings', 'usertutorial').get(id=cuid)
                except Users.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                return Response(get_response_data(user, cuid))

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
