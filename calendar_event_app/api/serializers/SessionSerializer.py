from rest_framework import serializers


class SessionSerializer(serializers.Serializer):
    id = serializers.CharField()
    userId = serializers.CharField()
    login = serializers.CharField()
    firstName = serializers.CharField()
    lastName = serializers.CharField()
    cronofyAccessToken = serializers.CharField()
    sfdcAccessToken = serializers.CharField()

