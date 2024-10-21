from rest_framework import status, viewsets, permissions, generics, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .enums import UserRole
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
    ProjectSerializer,
    TaskSerializer,
    DocumentSerializer,
    CommentSerializer,
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
        return Response(
            {"error": "Only managers can delete projects."},
            status=status.HTTP_400_BAD_REQUEST,
        )


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
        user = self.request.user

        if user.profile.role == UserRole.MANAGER.value:
            return self.queryset
        else:
            return self.queryset.filter(team_members=user)

    def create(self, request):
        user = request.user
        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can create projects."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user
        project = self.get_object()
        serializer = ProjectSerializer(
            project, data=request.data, context={"request": request}
        )
        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can update projects."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = request.user
        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can delete projects."},
                status=status.HTTP_403_FORBIDDEN,
            )

        project = self.get_object()
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_profile = user.profile

        if user_profile.role == UserRole.MANAGER.value:
            return self.queryset
        return self.queryset.filter(assignee=user_profile)

    def create(self, request):
        user = request.user
        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can create tasks."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user
        task = self.get_object()

        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can update tasks."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(task, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def perform_destroy(self, instance):
            user = self.request.user
            if user.profile.role != UserRole.MANAGER.value:
                return Response(
                    {"error": "Only managers can delete tasks."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            instance.delete()

    @action(detail=True, methods=["put"], permission_classes=[IsAuthenticated])
    def assign(self, request, pk=None):
        task = self.get_object()

        if request.user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can assign tasks."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Task assigned successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == UserRole.MANAGER.value:
            return self.queryset
        else:
            return self.queryset.filter(project__team_members=user)

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can create documents."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = request.user
        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can update documents."},
                status=status.HTTP_403_FORBIDDEN,
            )

        document = self.get_object()
        serializer = self.get_serializer(document, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can delete documents."},
                status=status.HTTP_403_FORBIDDEN,
            )

        document = self.get_object()
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == UserRole.MANAGER.value:
            return self.queryset
        else:
            return self.queryset.filter(author=user)

    def create(self, request):
        user = request.user
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = request.user
        comment = self.get_object()
        serializer = CommentSerializer(
            comment, data=request.data, context={"request": request}
        )
        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can update comments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = request.user
        if user.profile.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can delete comments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment = self.get_object()
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TimelineEventView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TimelineEventSerializer

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == UserRole.MANAGER.value:
            return TimelineEvent.objects.all().order_by("created_at")
        return TimelineEvent.objects.filter(project__team_members=user).order_by(
            "id", "created_at"
        )

    def get(self, request, project_id=None, *args, **kwargs):
        if project_id:
            if (
                request.user.profile.role == UserRole.MANAGER.value
                or Project.objects.filter(
                    id=project_id, team_members=request.user
                ).exists()
            ):
                queryset = TimelineEvent.objects.filter(project_id=project_id).order_by(
                    "created_at"
                )
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            return Response(
                {"error": "You do not have permission to view this timeline."},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)


class NotificationViewSet(viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def list(self, request):
        notifications = self.get_queryset()
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["put"],
        url_path="mark_read",
        url_name="mark-notification-read",
    )
    def mark_read(self, request, pk=None):
        notification = self.get_object(pk)
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, pk):
        return generics.get_object_or_404(Notification, id=pk, user=self.request.user)
