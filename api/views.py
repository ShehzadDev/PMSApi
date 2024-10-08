from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.views import APIView



# @api_view(["GET"])
# def api_overview(request):
#     api_urls = {
#         "Register": "/register/",
#         "Login": "/login/",
#         "Logout": "/logout/",
#     }
#     return Response(api_urls)


# @api_view(["POST"])
# def register(request):
#     serializer = RegisterSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.save()
#         token, created = Token.objects.get_or_create(user=user)
#         return Response(
#             {
#                 "token": token.key,
#                 "username": user.username,
#                 "email": user.email,
#             },
#             status=status.HTTP_201_CREATED,
#         )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["POST"])
# def login(request):
#     serializer = LoginSerializer(data=request.data)
#     if serializer.is_valid():
#         username = serializer.validated_data["username"]
#         password = serializer.validated_data["password"]
#         user = authenticate(username=username, password=password)
#         if user:
#             token, created = Token.objects.get_or_create(user=user)
#             return Response({"token": token.key}, status=status.HTTP_200_OK)
#         return Response(
#             {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
#         )
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["POST"])
# def logout(request):
#     if request.user.is_authenticated:
#         request.user.auth_token.delete()
#         return Response(
#             {"message": "Successfully logged out"}, status=status.HTTP_200_OK
#         )
#     return Response(
#         {"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
#     )


class APIOverview(APIView):
    def get(self, request):
        api_urls = {
            "Register": "/register/",
            "Login": "/login/",
            "Logout": "/logout/",
        }
        return Response(api_urls)


class Register(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
        )
