from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Task, Document, Comment, Profile


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "email"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["user", "profile_picture", "role", "contact_number"]
        depth = 1


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class AssignTaskSerializer(serializers.Serializer):
    team_member_id = serializers.IntegerField()

    def validate_team_member_id(self, value):
        if not Profile.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid team member ID.")
        return value


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"


# class CommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Comment
#         fields = "__all__"
