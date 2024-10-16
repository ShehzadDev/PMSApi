from .enums import UserRole
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Project,
    Task,
    Document,
    Comment,
    Profile,
    TimelineEvent,
    Notification,
)
from django.conf import settings


class RegisterSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    role = serializers.ChoiceField(choices=UserRole.choices())
    contact_number = serializers.CharField(required=False, max_length=15)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "profile_picture",
            "role",
            "contact_number",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        profile_picture = validated_data.pop("profile_picture", None)
        role = validated_data.pop("role")
        contact_number = validated_data.pop("contact_number", None)

        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        Profile.objects.create(
            user=user,
            profile_picture=profile_picture,
            role=role,
            contact_number=contact_number,
        )

        return user


class UserViewSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(
        source="profile.profile_picture", read_only=True
    )
    role = serializers.CharField(source="profile.role", read_only=True)
    contact_number = serializers.CharField(
        source="profile.contact_number", read_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "profile_picture",
            "role",
            "contact_number",
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user.profile.role not in [UserRole.MANAGER.value, UserRole.QA.value]:
            raise serializers.ValidationError(
                "Only managers and QA can update projects."
            )
        return super().update(instance, validated_data)


class TimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEvent
        fields = ["id", "project", "event_description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), required=False
    )

    class Meta:
        model = Task
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user
        if user.profile.role not in [UserRole.MANAGER.value, UserRole.QA.value]:
            raise serializers.ValidationError(
                "You don't have permission to create tasks."
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user.profile.role not in [UserRole.MANAGER.value, UserRole.QA.value]:
            raise serializers.ValidationError(
                "You don't have permission to update tasks."
            )
        return super().update(instance, validated_data)


class AssignTaskSerializer(serializers.Serializer):
    team_member_id = serializers.IntegerField()

    def validate_team_member_id(self, value):
        if not Profile.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid team member ID.")
        return value

    def assign_task(self, task):
        team_member_id = self.validated_data["team_member_id"]
        team_member_profile = Profile.objects.get(id=team_member_id)

        if not task.project.team_members.filter(id=team_member_profile.id).exists():
            raise serializers.ValidationError(
                "The team member is not part of the project."
            )

        task.assignee = team_member_profile
        task.save()
        return task


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["uploaded_by"]

    def create(self, validated_data):
        user = self.context["request"].user
        if user.profile.role not in [UserRole.MANAGER.value, UserRole.QA.value]:
            raise serializers.ValidationError(
                "You don't have permission to upload documents."
            )

        validated_data["uploaded_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user.profile.role not in [UserRole.MANAGER.value, UserRole.QA.value]:
            raise serializers.ValidationError(
                "You don't have permission to update documents."
            )

        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Comment
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user
        if user.profile.role not in [
            UserRole.MANAGER.value,
            UserRole.QA.value,
            UserRole.DEVELOPER.value,
        ]:
            raise serializers.ValidationError(
                "You don't have permission to add comments."
            )
        validated_data["author"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user.profile.role not in [
            UserRole.MANAGER.value,
            UserRole.QA.value,
            UserRole.DEVELOPER.value,
        ]:
            raise serializers.ValidationError(
                "You don't have permission to update comments."
            )
        return super().update(instance, validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "user", "message", "is_read", "created_at", "updated_at"]
        read_only_fields = ["is_read", "created_at", "updated_at"]

    def validate_message(self, value):
        if not value:
            raise serializers.ValidationError("Message cannot be empty.")
        return value

    def update(self, instance, validated_data):
        instance.is_read = validated_data.get("is_read", instance.is_read)
        instance.save()
        return instance
