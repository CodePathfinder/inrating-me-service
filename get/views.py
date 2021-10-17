from rest_framework.views import APIView
from rest_framework.exceptions import ParseError

from .mixins import RequestHelperMixin


class UserDetails(RequestHelperMixin, APIView):

    def post(self, request):

        # OAuth2 authentification check
        response = self.jwt_authentification(request)
        if isinstance(response, int):
            cuid = response
        else:
            return response

        # try and get user by request data/body args
        try:
            body = request.data
            return self.get_user_by_args(body, cuid)

        # if parsing error, current user information is provided
        except ParseError:
            return self.render_json_response(cuid, cuid)

    def get(self, request):

        # OAuth2 authentification check
        response = self.jwt_authentification(request)
        if isinstance(response, int):
            cuid = response
        else:
            return response

        # try and get user by request parameters
        try:
            params = request.GET
            return self.get_user_by_args(params, cuid)

        # if parsing error, current user information is provided
        except ParseError:
            return self.render_json_response(cuid, cuid)


class MeDetails(RequestHelperMixin, APIView):

    def post(self, request):

        response = self.jwt_authentification(request)
        return self.render_json_response(response, response) if isinstance(response, int) else response

    def get(self, request):

        response = self.jwt_authentification(request)
        return self.render_json_response(response, response) if isinstance(response, int) else response
