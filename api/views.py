from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Task, Profile, Project, Document, Comment
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProjectSerializer,
    TaskSerializer,
    DocumentSerializer,
    CommentSerializer,
    AssignTaskSerializer,
    UserViewSerializer,
)


class APIOverview(APIView):
    def get(self, request):
        api_urls = {
            "User Authentication": {
                "Register": "/api/register/",
                "Login": "/api/login/",
                "Logout": "/api/logout/",
                "Profile": "/api/profile/",
            },
            "Project Management": {
                "List Projects": "/api/projects/",
                "Create Project": "/api/projects/",
                "Retrieve/Update/Delete Project": "/api/projects/{id}/",
                "Project Timeline": "/api/projects/{id}/timeline/",
            },
            "Task Management": {
                "List Tasks": "/api/tasks/",
                "Create Task": "/api/tasks/",
                "Retrieve/Update/Delete Task": "/api/tasks/{id}/",
                "Assign Task": "/api/tasks/{id}/assign/",
            },
            "Document Management": {
                "List Documents": "/api/documents/",
                "Upload Document": "/api/documents/",
                "Retrieve/Update/Delete Document": "/api/documents/{id}/",
            },
            "Comment Management": {
                "List Comments": "/api/comments/",
                "Create Comment": "/api/comments/",
                "Retrieve/Update/Delete Comment": "/api/comments/{id}/",
            },
            "Timeline Events": {
                "List Timeline Events": "/api/timeline/",
            },
        }
        return Response(api_urls)


class Register(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            token, created = Token.objects.get_or_create(user=user)

            profile = Profile.objects.get(user=user)

            return Response(
                {
                    "token": token.key,
                    "username": user.username,
                    "email": user.email,
                    "profile_picture": (
                        profile.profile_picture.url if profile.profile_picture else None
                    ),
                    "role": profile.role,
                    "contact_number": profile.contact_number,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = UserViewSerializer(profile.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )


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


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(team_members=self.request.user.profile)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(project__team_members=self.request.user.profile)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def assign(self, request, pk=None):
        try:
            task = self.get_object()
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if request.user.profile.role != "manager":
            return Response(
                {"error": "You do not have permission to assign tasks."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssignTaskSerializer(data=request.data)
        if serializer.is_valid():
            team_member_id = serializer.validated_data["team_member_id"]

            try:
                team_member_profile = Profile.objects.get(id=team_member_id)
            except Profile.DoesNotExist:
                return Response(
                    {"error": "Profile not found for the given team member."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            task.assignee = team_member_profile
            task.save()

            return Response(
                {"message": "Task assigned successfully."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(project__team_members=self.request.user.profile)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(project__team_members=self.request.user.profile)
