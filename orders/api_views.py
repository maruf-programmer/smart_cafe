from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from core.models import Table, MenuItem, Staff
from .models import Order, OrderItem, Payment, WaiterCall
from .serializers import OrderSerializer, PaymentSerializer, WaiterCallSerializer


@api_view(['GET'])
def get_cart(request, table_id):
    cart = request.session.get(f'cart_{table_id}', [])
    cart_items = []
    total = 0
    for idx, c in enumerate(cart):
        subtotal = float(c['price']) * c['quantity'] * c['servings']
        cart_items.append({
            'index': idx,
            'item_id': c['item_id'],
            'name': c['name'],
            'price': c['price'],
            'servings': c['servings'],
            'quantity': c['quantity'],
            'subtotal': subtotal,
            'notes': c.get('notes', ''),
        })
        total += subtotal
    return Response({
        'cart_items': cart_items,
        'total_price': total
    })


@api_view(['POST'])
def add_to_cart(request, table_id):
    table = get_object_or_404(Table, id=table_id, is_active=True)
    item_id = request.data.get('item_id')
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    
    cart = request.session.get(f'cart_{table_id}', [])
    try:
        servings = int(request.data.get('servings', 1))
        quantity = int(request.data.get('quantity', 1))
    except (ValueError, TypeError):
        return Response({'error': 'Yaroqsiz qiymatlar'}, status=status.HTTP_400_BAD_REQUEST)
    
    notes = request.data.get('notes', '')

    cart.append({
        'item_id': item.id,
        'name': item.name,
        'price': str(item.price),
        'servings': servings,
        'quantity': quantity,
        'notes': notes,
    })

    request.session[f'cart_{table_id}'] = cart
    request.session.modified = True
    return Response({'status': 'success', 'message': f'{item.name} savatga qo\'shildi!'})


@api_view(['POST'])
def remove_from_cart(request, table_id, cart_index):
    cart = request.session.get(f'cart_{table_id}', [])
    if 0 <= cart_index < len(cart):
        removed_item = cart.pop(cart_index)
        request.session[f'cart_{table_id}'] = cart
        request.session.modified = True
        return Response({'status': 'success', 'message': f'{removed_item["name"]} savatdan olib tashlandi'})
    return Response({'error': 'Element topilmadi'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def checkout(request, table_id):
    table = get_object_or_404(Table, id=table_id, is_active=True)
    cart = request.session.get(f'cart_{table_id}', [])

    if not cart:
        return Response({'error': 'Savat bo\'sh!'}, status=status.HTTP_400_BAD_REQUEST)

    notes = request.data.get('notes', '')
    order = Order.objects.create(
        table=table,
        status='pending',
        notes=notes,
    )

    for c in cart:
        menu_item = MenuItem.objects.get(id=c['item_id'])
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=c['quantity'],
            servings=c['servings'],
            price_per_serving=menu_item.price,
            notes=c.get('notes', ''),
        )

    order.update_total()

    del request.session[f'cart_{table_id}']
    request.session.modified = True

    return Response({
        'status': 'success',
        'message': 'Buyurtma qabul qilindi! Iltimos kuting...',
        'order': OrderSerializer(order).data
    })


@api_view(['GET'])
def table_orders(request, table_id):
    table = get_object_or_404(Table, id=table_id, is_active=True)
    if table.current_session_start:
        orders = Order.objects.filter(table=table, created_at__gte=table.current_session_start).order_by('-created_at')
    else:
        orders = Order.objects.none()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
def complete_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.complete_order()
    return Response({'status': 'success', 'message': f'Buyurtma #{order.id} yakunlandi va stol bo\'shatildi.'})


@api_view(['POST'])
def process_payment_api(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    method = request.data.get('method', 'cash')
    amount = order.total_price

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={'amount': amount, 'method': method, 'status': 'pending'}
    )

    payment.method = method
    payment.transaction_id = f'TXN_{order.id}_{int(timezone.now().timestamp())}'

    payment.status = 'success'
    payment.completed_at = timezone.now()
    payment.save()

    order.status = 'delivered'
    order.save()

    return Response({
        'status': 'success',
        'message': 'To\'lov muvaffaqiyatli amalga oshirildi!',
        'payment': PaymentSerializer(payment).data
    })


@api_view(['POST'])
def call_waiter_api(request, table_id):
    table = get_object_or_404(Table, id=table_id, is_active=True)
    reason = request.data.get('reason', 'Mijoz chaqirdi')
    
    call = WaiterCall.objects.create(
        table=table,
        reason=reason,
    )
    
    # Barcha ofitsiantlarga SMS yuborish
    waiters = Staff.objects.filter(role='waiter', is_active=True)
    for waiter in waiters:
        waiter.send_sms(f"Stol {table.number} dan chaqiruv: {reason}")
        call.staff_phone += waiter.phone + ', '
    call.save()

    return Response({
        'status': 'success',
        'message': 'Ofitsiant chaqirildi.',
        'call': WaiterCallSerializer(call).data
    })


@api_view(['GET'])
def get_latest_call(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    latest_call = WaiterCall.objects.filter(table=table).order_by('-created_at').first()
    if latest_call:
        return Response(WaiterCallSerializer(latest_call).data)
    return Response({'message': 'Chaqiruvlar yo\'q'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reply_to_call_api(request, call_id):
    call = get_object_or_404(WaiterCall, id=call_id)
    message = request.data.get('reply_message', '')
    call.reply_with_message(message)
    return Response({'status': 'success', 'message': 'Javob yuborildi'})
