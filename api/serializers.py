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
from rest_framework.exceptions import ValidationError


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
        if user.profile.role != UserRole.MANAGER.value:
            raise serializers.ValidationError("Only managers can create projects.")
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


class AssignTaskSerializer(serializers.ModelSerializer):
    team_member_id = serializers.IntegerField()

    class Meta:
        model = Task
        fields = ["team_member_id"]

    def validate_assignee_id(self, value):
        if not Profile.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid team member ID.")
        return value

    def update(self, instance, validated_data):
        user = self.context["request"].user
        assignee_id = validated_data.get("team_member_id")

        if user.profile.role != UserRole.MANAGER.value:
            raise serializers.ValidationError("Only managers can assign tasks.")

        assignee_profile = Profile.objects.get(id=assignee_id)

        if not instance.project.team_members.filter(id=assignee_profile.id).exists():
            raise serializers.ValidationError(
                "The selected team member is not part of this project."
            )

        instance.assignee = assignee_profile
        instance.save()
        return instance


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "name",
            "file",
            "version",
            "project",
        ]

    def create(self, validated_data):
        user = self.context["request"].user

        if user.profile.role not in [UserRole.MANAGER.value, UserRole.QA.value]:
            raise serializers.ValidationError(
                "You don't have permission to upload documents."
            )

        document = Document.objects.create(**validated_data)
        return document

    def update(self, instance, validated_data):
        user = self.context["request"].user

        if user.profile.role not in [UserRole.MANAGER.value, UserRole.QA.value]:
            raise serializers.ValidationError(
                "You don't have permission to update documents."
            )

        return super().update(instance, validated_data)

    # def delete(self):
    #     user = self.context["request"].user

    #     if user.profile.role != UserRole.MANAGER.value:
    #         raise serializers.ValidationError("Only managers can delete documents.")

    #     self.instance.delete()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

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
        read_only_fields = ["user", "is_read", "created_at", "updated_at"]

    def validate_message(self, value):
        if self.instance is None and not value:
            raise serializers.ValidationError("Message cannot be empty.")
        return value

    def update(self, instance, validated_data):
        instance.is_read = True
        instance.save()
        return instance
