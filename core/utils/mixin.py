from typing import Any

from rest_framework import status
from rest_framework.response import Response


class BaseResponseMixin:
    """
    A mixin to standardize API responses for success and error cases.
    """

    def success_response(
        self,
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
    ):
        """
        Returns a standardized success response.
        """

        return Response(
            {"success": True, "message": message, "data": data}, status=status_code
        )

    def error_response(
        self,
        errors: Any = None,
        message: str = "An error occurred",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        """
        Returns a standardized error response.
        """

        return Response(
            {"success": False, "errors": errors, "message": message}, status=status_code
        )
