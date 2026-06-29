from rest_framework import serializers
from .models import Payment, Order, OrderItem, WaiterCall
from core.serializers import MenuItemSerializer, TableSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_detail = MenuItemSerializer(source='menu_item', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'menu_item_detail', 'quantity', 'servings', 'price_per_serving', 'subtotal', 'notes']
        read_only_fields = ['subtotal', 'price_per_serving']


class PaymentSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'method', 'method_display', 'status', 'status_display', 'transaction_id', 'created_at', 'completed_at']
        read_only_fields = ['transaction_id', 'created_at', 'completed_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table_detail = TableSerializer(source='table', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'table', 'table_detail', 'status', 'status_display', 'total_price', 'created_at', 'updated_at', 'completed_at', 'notes', 'items', 'payment']
        read_only_fields = ['total_price', 'created_at', 'updated_at', 'completed_at']


class WaiterCallSerializer(serializers.ModelSerializer):
    table_detail = TableSerializer(source='table', read_only=True)

    class Meta:
        model = WaiterCall
        fields = ['id', 'table', 'table_detail', 'reason', 'created_at', 'is_answered', 'answered_at', 'reply_message', 'staff_phone']
        read_only_fields = ['created_at', 'is_answered', 'answered_at', 'reply_message', 'staff_phone']
