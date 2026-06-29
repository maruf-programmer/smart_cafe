from rest_framework import serializers
from .models import Staff, Table, Category, MenuItem, Advertisement


class StaffSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'name', 'phone', 'role', 'role_display', 'is_active', 'qr_code']


class TableSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Table
        fields = ['id', 'number', 'status', 'status_display', 'is_active', 'qr_code', 'current_session_start']


class MenuItemSerializer(serializers.ModelSerializer):
    prep_time_display = serializers.CharField(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'category', 'price', 'image', 'images', 'is_available',
            'prep_time_minutes', 'prep_time_display', 'serving_options', 'ingredients',
            'vitamins', 'weight_grams', 'calories', 'is_popular'
        ]


class CategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'prep_time_minutes', 'is_active', 'order', 'items']


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'description', 'image', 'is_active', 'display_order', 'link', 'created_at']
