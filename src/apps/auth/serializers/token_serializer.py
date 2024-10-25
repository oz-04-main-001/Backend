from rest_framework import serializers


class TokenSerializer(serializers.Serializer):

    def validate(self, data: dict) -> dict:
        access_token = self.context.get("access_token")

        if not access_token:
            raise serializers.ValidationError("Access token is required.")

        data["access_token"] = access_token

        return data
