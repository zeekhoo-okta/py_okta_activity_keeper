from rest_framework import serializers


class sfdc_login(object):
    def __init__(self, username, password, security_token):
        self.username = username
        self.password = password
        self.security_token = security_token


class sfdc_login_serializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=50)
    security_token = serializers.CharField(max_length=200, required=False)

    def create(self, validated_data):
        return sfdc_login.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.security_token = validated_data.get('security_token', instance.security_token)
        instance.save()
        return instance

