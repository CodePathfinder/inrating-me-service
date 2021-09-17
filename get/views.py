from django.shortcuts import HttpResponse
# from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

import json
import base64

from .models import Users
from .resources import get_response_data
from . import const
from .request_helpers import timestamp_token_verification, verify_user_status


def index(request):
    return HttpResponse('<h2>TEST CONNECTION</h2>')


class UserDetails(APIView):

    @method_decorator(cache_page(60 * 5))
    def post(self, request):

        # check if 'Authorization' key in request.headers dict
        if 'Authorization' in request.headers and request.headers['Authorization']:

            try:
                # get value of 'Authorization' key and get rid of 'Bearer ' substring
                token = (request.headers['Authorization']).split(' ')[1]

                # split token string by (.) and extract encripted payload data
                token_data = token.split('.')[1]

            except IndexError:
                return Response(
                    {'Error': "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)

            # decode payload data(b64decode) and convert JSON string to dictionary(json.loads)
            try:
                data = json.loads(base64.b64decode(token_data + '=='))

            except json.decoder.JSONDecodeError:
                return Response(
                    {'Error': "Invalid token. JSONDecodeError"}, status=status.HTTP_401_UNAUTHORIZED)

            if not timestamp_token_verification(data):
                return Response(
                    {'Error': "Token is expired."}, status=status.HTTP_401_UNAUTHORIZED)

            # extract 'current user id' (cuid) from payload data
            if 'sub' in data:
                cuid = int(data['sub'])
            else:
                return Response(
                    {'Error': "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                body = request.data
            # if parsing error, current user information is provided
            except ParseError:
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
            return Response({'Error': "No token."}, status=status.HTTP_401_UNAUTHORIZED)

    @method_decorator(cache_page(60 * 5))
    def get(self, request):

        # check if 'Authorization' key in request.headers dict
        if 'Authorization' in request.headers and request.headers['Authorization']:

            try:
                # get value of 'Authorization' key and get rid of 'Bearer ' substring
                token = (request.headers['Authorization']).split(' ')[1]

                # split token string by (.) and extract encripted payload data
                token_data = token.split('.')[1]

            except IndexError:
                return Response(
                    {'Error': "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)

            # decode payload data(b64decode) and convert JSON string to dictionary(json.loads)
            try:
                data = json.loads(base64.b64decode(token_data + '=='))

            except json.decoder.JSONDecodeError:
                return Response(
                    {'Error': "Invalid token. JSONDecodeError"}, status=status.HTTP_401_UNAUTHORIZED)

            if not timestamp_token_verification(data):
                return Response(
                    {'Error': "Token is invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)

            # extract 'current user id' (cuid) from payload data
            if 'sub' in data:
                cuid = int(data['sub'])
            else:
                return Response(
                    {'Error': "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                params = request.GET
            # if parsing error, current user information is provided
            except ParseError:
                uid, unavalable_reason = verify_user_status(cuid, cuid)
                if unavalable_reason:
                    return Response({'status': const.unavailable_user_status_codes[unavalable_reason]}, status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response(get_response_data(uid, cuid))
            else:
                # if 'nickname' in request.data, validate 'nickname', try and extract user data by 'nickname'
                if 'nickname' in params and params["nickname"]:
                    if not isinstance(params["nickname"], str):
                        return Response(
                            {'ValidationError': "nickname should be a string."}, status=status.HTTP_400_BAD_REQUEST)
                    if len(params["nickname"]) > 255:
                        return Response(
                            {'ValidationError': "max lenght of nickname should be 255."}, status=status.HTTP_400_BAD_REQUEST)

                    user = Users.objects.filter(
                        nickname=params["nickname"]).first()
                    if user:
                        uid, unavalable_reason = verify_user_status(
                            user.id, cuid)
                        if unavalable_reason:
                            return Response({'status': const.unavailable_user_status_codes[unavalable_reason]}, status=status.HTTP_403_FORBIDDEN)
                        else:
                            return Response(get_response_data(uid, cuid))
                    elif 'id' not in params or not params["id"]:
                        return Response({'status': const.unavailable_user_status_codes['not_found']}, status=status.HTTP_403_FORBIDDEN)

                # if 'id' in request.data, try and extract user data by 'id'
                if 'id' in params and params["id"]:
                    try:
                        id = int(params["id"])
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
            return Response({'Error': "No token."}, status=status.HTTP_401_UNAUTHORIZED)


class MeDetails(APIView):

    @method_decorator(cache_page(60 * 5))
    def post(self, request):

        # check if 'Authorization' key in request.headers dict
        if 'Authorization' in request.headers and request.headers['Authorization']:

            try:
                # get value of 'Authorization' key and get rid of 'Bearer ' substring
                token = (request.headers['Authorization']).split(' ')[1]

                # split token string by (.) and extract encripted payload data
                token_data = token.split('.')[1]

            except IndexError:
                return Response(
                    {'Error': "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)

            # decode payload data(b64decode) and convert JSON string to dictionary(json.loads)
            try:
                data = json.loads(base64.b64decode(token_data + '=='))

            except json.decoder.JSONDecodeError:
                return Response(
                    {'Error': "Invalid token. JSONDecodeError"}, status=status.HTTP_401_UNAUTHORIZED)

            if not timestamp_token_verification(data):
                return Response(
                    {'Error': "Token is invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)

            # extract 'current user id' (cuid) from payload data
            if 'sub' in data:
                cuid = int(data['sub'])
            else:
                return Response(
                    {'Error': "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

            uid, unavalable_reason = verify_user_status(cuid, cuid)
            if unavalable_reason:
                return Response({'status': const.unavailable_user_status_codes[unavalable_reason]}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(get_response_data(uid, cuid))
        else:
            return Response({'Error': "No token."}, status=status.HTTP_401_UNAUTHORIZED)

    @method_decorator(cache_page(60 * 5))
    def get(self, request):

        # check if 'Authorization' key in request.headers dict
        if 'Authorization' in request.headers and request.headers['Authorization']:

            try:
                # get value of 'Authorization' key and get rid of 'Bearer ' substring
                token = (request.headers['Authorization']).split(' ')[1]

                # split token string by (.) and extract encripted payload data
                token_data = token.split('.')[1]

            except IndexError:
                return Response(
                    {'Error': "Invalid token format."}, status=status.HTTP_401_UNAUTHORIZED)

            # decode payload data(b64decode) and convert JSON string to dictionary(json.loads)
            try:
                data = json.loads(base64.b64decode(token_data + '=='))

            except json.decoder.JSONDecodeError:
                return Response(
                    {'Error': "Invalid token. JSONDecodeError"}, status=status.HTTP_401_UNAUTHORIZED)

            if not timestamp_token_verification(data):
                return Response(
                    {'Error': "Token is invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)

            # extract 'current user id' (cuid) from payload data
            if 'sub' in data:
                cuid = int(data['sub'])
            else:
                return Response(
                    {'Error': "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

            uid, unavalable_reason = verify_user_status(cuid, cuid)
            if unavalable_reason:
                return Response({'status': const.unavailable_user_status_codes[unavalable_reason]}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(get_response_data(uid, cuid))
        else:
            return Response({'Error': "No token."}, status=status.HTTP_401_UNAUTHORIZED)
