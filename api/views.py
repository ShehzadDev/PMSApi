from rest_framework import status, viewsets, permissions, generics, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import (
    Task,
    Profile,
    Project,
    Document,
    Comment,
    TimelineEvent,
    Notification,
)
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProjectSerializer,
    TaskSerializer,
    DocumentSerializer,
    CommentSerializer,
    AssignTaskSerializer,
    UserViewSerializer,
    TimelineEventSerializer,
    NotificationSerializer,
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

            refresh = RefreshToken.for_user(user)
            profile = Profile.objects.get(user=user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
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

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = UserViewSerializer(profile.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(team_members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TimelineEventListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TimelineEventSerializer

    def get_queryset(self):
        return TimelineEvent.objects.all().order_by("created_at")


class TimelineEventDetailView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TimelineEventSerializer

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return TimelineEvent.objects.filter(project_id=project_id).order_by(
            "created_at"
        )


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == "manager":
            return self.queryset
        return self.queryset.filter(project__team_members=user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def assign(self, request, pk=None):
        try:
            task = Task.objects.get(id=pk)
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
            try:
                serializer.assign_task(task)
                return Response(
                    {"message": "Task assigned successfully."},
                    status=status.HTTP_200_OK,
                )
            except serializers.ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(project__team_members=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(project__team_members=self.request.user)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return generics.get_object_or_404(
            Notification, id=self.kwargs["notification_id"], user=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(is_read=True)
