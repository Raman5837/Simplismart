from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils.mixin import BaseResponseMixin


class TokenAPIView(APIView, BaseResponseMixin):
    """
    Handles JWT Authentication (Login)
    """

    def post(self, request: Request) -> Response:
        """
        Login and get JWT token
        """

        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return self.error_response(message="Invalid Payload")

        user = User.objects.filter(username=username).first()

        if not user:
            return self.error_response(
                message="User not found.", status_code=status.HTTP_404_NOT_FOUND
            )

        if not user.check_password(password):
            return self.error_response(
                message="Invalid credentials.", status_code=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token["user_id"] = user.id

        return self.success_response(data={"access_token": str(access_token)})
