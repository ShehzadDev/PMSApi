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

    def validate(self, attrs):
        request_user = self.context["request"].user

        if "created_by" in attrs and attrs["created_by"] != request_user:
            raise ValidationError("You can only create a Project for yourself.")

        if attrs["start_date"] > attrs["end_date"]:
            raise ValidationError("End date should be greater than start date.")

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), required=False
    )
    team_member_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Task
        fields = "__all__"

    def validate(self, attrs):
        user = self.context["request"].user

        if "team_member_id" in attrs:
            if user.profile.role != UserRole.MANAGER.value:
                raise serializers.ValidationError("Only managers can assign tasks.")

            try:
                assignee_profile = Profile.objects.get(id=attrs["team_member_id"])
            except Profile.DoesNotExist:
                raise serializers.ValidationError("Invalid team member selected.")

            if not self.instance.project.team_members.filter(
                id=assignee_profile.id
            ).exists():
                raise serializers.ValidationError(
                    "The selected team member is not part of this project."
                )

            attrs["assignee"] = assignee_profile

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


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

    def validate(self, attrs):
        user = self.context["request"].user

        project_id = attrs.get("project")
        if project_id:
            if user.profile.role != UserRole.MANAGER.value:
                if not Document.objects.filter(
                    project=project_id, project__team_members=user
                ).exists():
                    raise serializers.ValidationError(
                        "You do not have permission to add documents to this project."
                    )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"


class TimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEvent
        fields = ["id", "project", "event_description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "user", "message", "is_read", "created_at", "updated_at"]
        read_only_fields = ["user", "is_read", "created_at", "updated_at"]
