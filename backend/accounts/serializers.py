from django.contrib.auth.models import User
from rest_framework import serializers

from olympiad.models import Center
from .models import AdminProfile


def get_default_center():
    center, _ = Center.objects.get_or_create(name='LIDER.Uz Onlayn Olimpiada')
    return center


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, required=False)
    center = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    center_name = serializers.CharField(source='admin_profile.center.name', read_only=True)
    is_main_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'password',
            'is_staff', 'is_superuser', 'is_main_admin', 'center', 'center_name',
            'date_joined'
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'is_main_admin', 'center_name', 'date_joined']

    def get_is_main_admin(self, obj):
        profile = getattr(obj, 'admin_profile', None)
        return bool(obj.is_superuser or not profile or not profile.center_id)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile = getattr(instance, 'admin_profile', None)
        data['center'] = getattr(profile, 'center_id', None) if profile else None
        data['center_name'] = getattr(getattr(profile, 'center', None), 'name', '') if profile else ''
        return data

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST' and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'Parol kiritish majburiy.'})
        attrs.pop('center', None)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.is_staff = True
        user.is_superuser = False
        user.set_password(password)
        user.save()
        AdminProfile.objects.create(user=user, center=get_default_center(), branch='')
        return user
