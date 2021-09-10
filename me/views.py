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
from . import const


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

                # get request.data containing either request.body (json) or request.POST (form) data
                try:
                    body = request.data
                # if request.data containing either request.body (json) or request.POST (form) data
                except Exception:
                    uid, unavalable_reason = verify_user_status(cuid, cuid)
                    if unavalable_reason:
                        return Response({'status': const.unavailable_user_status_codes[unavalable_reason]}, status=status.HTTP_403_FORBIDDEN)
                    else:
                        return Response(get_response_data(uid, cuid))
                else:
                    # if 'nickname' in request.data, validate 'nickname', try and extract user data by 'nickname'
                    if 'nickname' in body and body["nickname"]:
                        if not isinstance(body["nickname"], str):
                            return Response(
                                {'ValidationError': "nickname should be a string."}, status=status.HTTP_400_BAD_REQUEST)
                        if len(body["nickname"]) > 255:
                            return Response(
                                {'ValidationError': "max lenght of nickname should be 255."}, status=status.HTTP_400_BAD_REQUEST)

                        user = Users.objects.filter(
                            nickname=body["nickname"]).first()
                        if user:
                            uid, unavalable_reason = verify_user_status(
                                user.id, cuid)
                            if unavalable_reason:
                                return Response({'status': const.unavailable_user_status_codes[unavalable_reason]}, status=status.HTTP_403_FORBIDDEN)
                            else:
                                return Response(get_response_data(uid, cuid))
                        elif 'id' not in body or not body["id"]:
                            return Response({'status': const.unavailable_user_status_codes['not_found']}, status=status.HTTP_403_FORBIDDEN)

                    # if 'id' in request.data, try and extract user data by 'id'
                    if 'id' in body and body["id"]:
                        try:
                            id = int(body["id"])
                        except ValueError:
                            return Response(
                                {'ValidationError': "id should be an integer."}, status=status.HTTP_400_BAD_REQUEST)
                        uid, unavalable_reason = verify_user_status(id, cuid)
                        if unavalable_reason:
                            return Response({'status': const.unavailable_user_status_codes[unavalable_reason]}, status=status.HTTP_403_FORBIDDEN)
                        else:
                            return Response(get_response_data(uid, cuid))

                    # extract user data by 'current user id' if neither nickname nor id is provided in request.data
                    uid, unavalable_reason = verify_user_status(cuid, cuid)
                    if unavalable_reason:
                        return Response({'status': const.unavailable_user_status_codes[unavalable_reason]}, status=status.HTTP_403_FORBIDDEN)
                    else:
                        return Response(get_response_data(uid, cuid))

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


def verify_user_status(id, cuid):
    unavailable_reasons = [item[0]
                           for item in const.unavailable_user_status_codes.items()]
    unaval_reason = ''
    user = Users.objects.filter(id=id).first()
    if not user:
        unaval_reason = 'not_found'
        return ((None, unaval_reason))
    elif id == cuid:
        return ((cuid, unaval_reason))
    elif user.status.replace(' ', '_') in unavailable_reasons:
        unaval_reason = user.status.replace(' ', '_')
        return ((id, unaval_reason))
    elif user.userblacklist_set.filter(blocked_user_id=cuid).exists():
        unaval_reason = 'blacklist'
        return ((id, unaval_reason))
    else:
        return ((id, unaval_reason))
