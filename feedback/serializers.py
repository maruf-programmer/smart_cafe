from rest_framework import serializers
from .models import Feedback
from core.serializers import TableSerializer


class FeedbackSerializer(serializers.ModelSerializer):
    table_detail = TableSerializer(source='table', read_only=True)
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'table', 'table_detail', 'rating', 'rating_display', 'comment', 'menu_item_name', 'is_anonymous', 'created_at']
        read_only_fields = ['created_at']
