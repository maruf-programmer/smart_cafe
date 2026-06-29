from django.shortcuts import render


def call_waiter(request, table_id):
    return render(request, 'orders/call_waiter.html', {'table_id': table_id})


def payment_page(request, order_id):
    return render(request, 'orders/payment.html', {'order_id': order_id})
