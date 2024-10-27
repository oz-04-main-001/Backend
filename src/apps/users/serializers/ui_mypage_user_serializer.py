from rest_framework import serializers

from apps.users.models import User


class MyPageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "user_type",
            "name",
            "phone_number",
            "email",
        ]
