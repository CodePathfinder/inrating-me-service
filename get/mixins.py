from rest_framework.response import Response
from rest_framework import status

import json
import base64
import time
from .models import Users
from . import const
from .resources import get_response_data


class RequestHelperMixin(object):

    def jwt_authentification(self, request):
        """ OAuth2 authentification check """

        # check if 'Authorization' key in request.headers dict
        if 'Authorization' in request.headers and request.headers['Authorization']:

            try:
                # get value of 'Authorization' key and extract encripted payload data
                token_data = (request.headers['Authorization']).split('.')[1]
                print(token_data)

            except IndexError:
                return Response({'Error': 'Invalid token format.'}, status=status.HTTP_401_UNAUTHORIZED)

            # decode payload data(b64decode) and convert JSON string to dictionary(json.loads)
            try:
                data = json.loads(base64.b64decode(token_data + '=='))

            except json.decoder.JSONDecodeError:
                return Response({'Error': 'Invalid token. JSONDecodeError'}, status=status.HTTP_401_UNAUTHORIZED)
            except UnicodeDecodeError:
                return Response({'Error': 'Invalid token. UnicodeDecodeError'}, status=status.HTTP_401_UNAUTHORIZED)

            if not self.timestamp_token_verification(data):
                return Response({'Error': 'Token is expired.'}, status=status.HTTP_401_UNAUTHORIZED)

            # extract 'current user id' (cuid) from payload data
            if 'sub' in data:
                cuid = int(data['sub'])
                return cuid
            else:
                return Response({'Error': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'Error': 'No token.'}, status=status.HTTP_401_UNAUTHORIZED)

    def timestamp_token_verification(self, data):
        """ check if authorization token is not expired """

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

    def verify_user_status(self, id, cuid):
        """ check if unavailable_reason """

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

    def render_json_response(self, id, cuid):
        """ check authorization and render json response """

        uid, unavalable_reason = self.verify_user_status(id, cuid)
        if unavalable_reason:
            return Response({'status': const.unavailable_user_status_codes[unavalable_reason]}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(get_response_data(uid, cuid))

    def get_user_by_args(self, dict, cuid):
        # if 'nickname' in dict, validate 'nickname', try and extract user data by 'nickname'
        if 'nickname' in dict and dict["nickname"]:
            if not isinstance(dict["nickname"], str):
                return Response(
                    {'ValidationError': "nickname should be a string."}, status=status.HTTP_400_BAD_REQUEST)
            if len(dict["nickname"]) > 255:
                return Response(
                    {'ValidationError': "max lenght of nickname should be 255."}, status=status.HTTP_400_BAD_REQUEST)

            user = Users.objects.filter(
                nickname=dict["nickname"]).first()
            if user:
                return self.render_json_response(user.id, cuid)

            elif 'id' not in dict or not dict["id"]:
                return Response({'status': const.unavailable_user_status_codes['not_found']}, status=status.HTTP_403_FORBIDDEN)

        # if 'id' in dict, try and extract user data by 'id'
        if 'id' in dict and dict["id"]:
            try:
                id = int(dict["id"])
                return self.render_json_response(id, cuid)
            except ValueError:
                return Response(
                    {'ValidationError': "id should be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        # extract user data by 'current user id' if neither nickname nor id is provided in dict
        return self.render_json_response(cuid, cuid)
