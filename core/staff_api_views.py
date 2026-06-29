from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Sum
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from core.models import Table, Staff, Category, MenuItem
from orders.models import Order, WaiterCall
from feedback.models import Feedback
from core.serializers import TableSerializer, StaffSerializer, CategorySerializer, MenuItemSerializer
from orders.serializers import OrderSerializer, WaiterCallSerializer
from feedback.serializers import FeedbackSerializer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    total_tables = Table.objects.count()
    free_tables = Table.objects.filter(status='free').count()
    occupied_tables = Table.objects.filter(status='occupied').count()
    total_staff = Staff.objects.filter(is_active=True).count()

    pending_orders = Order.objects.exclude(status__in=['completed', 'cancelled']).count()
    today_completed = Order.objects.filter(
        status='completed',
        completed_at__date=timezone.now().date()
    ).count()

    waiter_calls_count = WaiterCall.objects.filter(is_answered=False).count()

    pending_orders_list = Order.objects.exclude(
        status__in=['completed', 'cancelled']
    ).select_related('table').order_by('-created_at')[:5]

    waiter_calls_list = WaiterCall.objects.filter(is_answered=False).select_related('table').order_by('-created_at')[:5]

    active_tables = Table.objects.filter(status='occupied').order_by('-current_session_start')[:5]

    recent_feedback = Feedback.objects.all().select_related('table').order_by('-created_at')[:5]

    return Response({
        'total_tables': total_tables,
        'free_tables': free_tables,
        'occupied_tables': occupied_tables,
        'total_staff': total_staff,
        'pending_orders': pending_orders,
        'today_completed': today_completed,
        'waiter_calls_count': waiter_calls_count,
        'pending_orders_list': OrderSerializer(pending_orders_list, many=True).data,
        'waiter_calls_list': WaiterCallSerializer(waiter_calls_list, many=True).data,
        'active_tables': TableSerializer(active_tables, many=True).data,
        'recent_feedback': FeedbackSerializer(recent_feedback, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def order_list_api(request):
    status_filter = request.query_params.get('status')
    orders = Order.objects.all().select_related('table').prefetch_related('items__menu_item')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    else:
        orders = orders.exclude(status__in=['completed', 'cancelled'])

    serializer = OrderSerializer(orders, many=True)
    return Response({
        'orders': serializer.data,
        'status_choices': dict(Order.STATUS_CHOICES),
        'current_status': status_filter
    })


@api_view(['POST', 'PATCH'])
@permission_classes([IsAdminUser])
def update_order_status_api(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.data.get('status')
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        if new_status == 'completed':
            order.complete_order()
        order.save()
        return Response({
            'status': 'success', 
            'message': f"Buyurtma #{order.id} holati '{order.get_status_display()}'ga o'zgartirildi.",
            'order': OrderSerializer(order).data
        })
    return Response({'error': 'Yaroqsiz holat kiritildi'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def waiter_calls_api(request):
    calls = WaiterCall.objects.all().select_related('table').order_by('-is_answered', '-created_at')
    serializer = WaiterCallSerializer(calls, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def resolve_call_api(request, call_id):
    call = get_object_or_404(WaiterCall, id=call_id)
    message = request.data.get('reply_message', 'Xodim yo\'lda')
    call.reply_with_message(message)
    return Response({
        'status': 'success', 
        'message': f"Stol #{call.table.number} chaqiruviga javob berildi.",
        'call': WaiterCallSerializer(call).data
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def menu_management_api(request):
    categories = Category.objects.all().prefetch_related('items')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def menu_item_add_api(request):
    name = request.data.get('name')
    category_id = request.data.get('category')
    price = request.data.get('price')
    description = request.data.get('description', '')
    
    if not name or not category_id or not price:
        return Response({'error': 'Nom, kategoriya va narx majburiy'}, status=status.HTTP_400_BAD_REQUEST)
        
    category = get_object_or_404(Category, id=category_id)
    
    image = request.data.get('image', '')
    images = request.data.get('images', [])
    if not isinstance(images, list):
        images = [images] if images else []
    images = [img for img in images if img][:10]
    
    # Use first image in the list as cover image if no primary image is specified
    if not image and images:
        image = images[0]
        
    prep_time_minutes = int(request.data.get('prep_time_minutes', 20) or 20)
    ingredients = request.data.get('ingredients', '')
    vitamins = request.data.get('vitamins', '')
    weight_grams = int(request.data.get('weight_grams', 250) or 250)
    calories = int(request.data.get('calories', 0) or 0)
    is_popular = request.data.get('is_popular') is True or request.data.get('is_popular') == 'true'
    is_available = request.data.get('is_available') is True or request.data.get('is_available') == 'true'
    
    serving_options = request.data.get('serving_options', [])
    if isinstance(serving_options, str):
        try:
            serving_options = [float(x.strip()) for x in serving_options.split(',') if x.strip()]
        except ValueError:
            serving_options = [1.0]

    item = MenuItem.objects.create(
        name=name,
        category=category,
        price=price,
        description=description,
        is_available=is_available,
        image=image,
        images=images,
        prep_time_minutes=prep_time_minutes,
        serving_options=serving_options,
        ingredients=ingredients,
        vitamins=vitamins,
        weight_grams=weight_grams,
        calories=calories,
        is_popular=is_popular
    )
    return Response({
        'status': 'success', 
        'message': f"'{name}' menyuga qo'shildi.",
        'item': MenuItemSerializer(item).data
    })


@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def menu_item_edit_api(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    
    name = request.data.get('name')
    category_id = request.data.get('category')
    price = request.data.get('price')
    description = request.data.get('description')
    is_available = request.data.get('is_available')
    image = request.data.get('image')
    images = request.data.get('images')
    prep_time_minutes = request.data.get('prep_time_minutes')
    serving_options = request.data.get('serving_options')
    ingredients = request.data.get('ingredients')
    vitamins = request.data.get('vitamins')
    weight_grams = request.data.get('weight_grams')
    calories = request.data.get('calories')
    is_popular = request.data.get('is_popular')

    if name: item.name = name
    if category_id: item.category_id = category_id
    if price: item.price = price
    if description is not None: item.description = description
    if is_available is not None: 
        item.is_available = is_available is True or is_available == 'true'
    if image is not None: item.image = image
    
    if images is not None:
        if not isinstance(images, list):
            images = [images] if images else []
        item.images = [img for img in images if img][:10]
        if not item.image and item.images:
            item.image = item.images[0]

    if prep_time_minutes is not None: item.prep_time_minutes = int(prep_time_minutes or 20)
    if ingredients is not None: item.ingredients = ingredients
    if vitamins is not None: item.vitamins = vitamins
    if weight_grams is not None: item.weight_grams = int(weight_grams or 250)
    if calories is not None: item.calories = int(calories or 0)
    if is_popular is not None:
        item.is_popular = is_popular is True or is_popular == 'true'
        
    if serving_options is not None:
        if isinstance(serving_options, str):
            try:
                serving_options = [float(x.strip()) for x in serving_options.split(',') if x.strip()]
            except ValueError:
                serving_options = [1.0]
        item.serving_options = serving_options
        
    item.save()
    return Response({
        'status': 'success', 
        'message': f"'{item.name}' tahrirlandi.",
        'item': MenuItemSerializer(item).data
    })


@api_view(['DELETE', 'POST'])
@permission_classes([IsAdminUser])
def menu_item_delete_api(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    name = item.name
    item.delete()
    return Response({
        'status': 'success',
        'message': f"'{name}' menyudan butunlay o'chirildi."
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def table_management_api(request):
    tables = Table.objects.all().order_by('number')
    serializer = TableSerializer(tables, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_table_api(request):
    number = request.data.get('number')
    if not number:
        return Response({'error': 'Stol raqami kiritilishi shart'}, status=status.HTTP_400_BAD_REQUEST)
        
    if Table.objects.filter(number=number).exists():
        return Response({'error': f"Stol #{number} allaqachon mavjud."}, status=status.HTTP_400_BAD_REQUEST)
        
    table = Table.objects.create(number=number)
    return Response({
        'status': 'success', 
        'message': f"Stol #{number} muvaffaqiyatli qo'shildi.",
        'table': TableSerializer(table).data
    })


@api_view(['DELETE', 'POST'])
@permission_classes([IsAdminUser])
def delete_table_api(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    num = table.number
    table.delete()
    return Response({
        'status': 'success',
        'message': f"Stol #{num} muvaffaqiyatli o'chirildi."
    })


@api_view(['POST', 'PATCH'])
@permission_classes([IsAdminUser])
def update_table_status_api(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    new_status = request.data.get('status')
    if new_status in dict(Table.STATUS_CHOICES):
        table.status = new_status
        if new_status == 'free':
            table.current_session_start = None
        elif new_status == 'occupied' and not table.current_session_start:
            table.current_session_start = timezone.now()
        table.save()
        return Response({
            'status': 'success', 
            'message': f"Stol #{table.number} holati yangilandi.",
            'table': TableSerializer(table).data
        })
    return Response({'error': 'Yaroqsiz holat'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def upload_image_api(request):
    if 'image' not in request.FILES:
        return Response({'error': 'Rasm fayli yuborilmadi'}, status=status.HTTP_400_BAD_REQUEST)
        
    image_file = request.FILES['image']
    file_name = default_storage.save(f"menu/{image_file.name}", ContentFile(image_file.read()))
    file_url = f"/{settings.MEDIA_URL.lstrip('/')}{file_name}"
    return Response({
        'status': 'success',
        'url': file_url
    })
