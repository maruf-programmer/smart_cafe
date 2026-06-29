from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
import os
from .models import Table, Category, MenuItem, Advertisement, Staff
from orders.models import Order
from .serializers import TableSerializer, CategorySerializer, MenuItemSerializer, AdvertisementSerializer, StaffSerializer


@api_view(['GET'])
def home_stats(request):
    tables = Table.objects.filter(is_active=True)
    ads = Advertisement.objects.filter(is_active=True)
    
    today = timezone.now().date()
    customers_today = Order.objects.filter(
        status='completed',
        completed_at__date=today
    ).count()

    all_items = MenuItem.objects.filter(is_available=True).order_by('price')
    cheapest_item = all_items.first()
    expensive_item = all_items.last()
    popular_items = MenuItem.objects.filter(is_available=True, is_popular=True)[:3]

    free_tables = tables.filter(status='free').count()
    occupied_tables = tables.filter(status='occupied').count()

    return Response({
        'free_tables': free_tables,
        'occupied_tables': occupied_tables,
        'total_tables_count': tables.count(),
        'customers_today': customers_today,
        'cheapest_item': MenuItemSerializer(cheapest_item).data if cheapest_item else None,
        'expensive_item': MenuItemSerializer(expensive_item).data if expensive_item else None,
        'popular_items': MenuItemSerializer(popular_items, many=True).data,
    })


@api_view(['GET'])
def table_list(request):
    tables = Table.objects.filter(is_active=True)
    serializer = TableSerializer(tables, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def occupy_table(request, table_id):
    table = get_object_or_404(Table, id=table_id, is_active=True)
    if table.status == 'free':
        table.occupy()
        return Response({'status': 'success', 'message': f'Stol #{table.number} band qilindi. Xush kelibsiz!'})
    elif table.status == 'cleaning':
        return Response({'status': 'warning', 'message': 'Stol tozalanmoqda, iltimos kuting...'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 'success', 'message': 'Stol allaqachon band.'})


@api_view(['POST'])
def free_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    from orders.models import Order
    from django.utils import timezone
    Order.objects.filter(
        table=table,
        status__in=['pending', 'confirmed', 'preparing', 'ready', 'delivered']
    ).update(status='completed', completed_at=timezone.now())
    table.free_table()
    return Response({'status': 'success', 'message': f'Stol #{table.number} tozalanmoqda.'})


@api_view(['POST'])
def mark_free(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    table.mark_free()
    return Response({'status': 'success', 'message': f'Stol #{table.number} bo\'shashdi!'})


@api_view(['GET'])
def category_list(request):
    categories = Category.objects.filter(is_active=True)
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def menu_item_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    serializer = MenuItemSerializer(item)
    return Response(serializer.data)


@api_view(['GET'])
def advertisement_list(request):
    ads = Advertisement.objects.filter(is_active=True)
    serializer = AdvertisementSerializer(ads, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def active_waiters(request):
    waiters = Staff.objects.filter(role='waiter', is_active=True)
    serializer = StaffSerializer(waiters, many=True)
    return Response(serializer.data)


def schema_view(request):
    yaml_path = os.path.join(settings.BASE_DIR, 'openapi.yaml')
    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/yaml')


def swagger_ui_view(request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Smart Cafe API Swagger UI</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            window.onload = () => {
                window.ui = SwaggerUIBundle({
                    url: '/api/schema/',
                    dom_id: '#swagger-ui',
                });
            };
        </script>
    </body>
    </html>
    """
    return HttpResponse(html, content_type='text/html')


def redoc_ui_view(request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Smart Cafe API ReDoc</title>
        <style>
            body { margin: 0; padding: 0; }
        </style>
    </head>
    <body>
        <redoc spec-url='/api/schema/'></redoc>
        <script src="https://unpkg.com/redoc@2.0.0-rc.77/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """
    return HttpResponse(html, content_type='text/html')
