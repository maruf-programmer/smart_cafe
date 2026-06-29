from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def menu(request, table_id):
    return render(request, 'core/menu.html', {'table_id': table_id})


def item_detail(request, table_id, item_id):
    return render(request, 'core/item_detail.html', {'table_id': table_id, 'item_id': item_id})


def cart(request, table_id):
    return render(request, 'core/cart.html', {'table_id': table_id})


def my_orders(request, table_id):
    return render(request, 'core/my_orders.html', {'table_id': table_id})


def complete_session(request, table_id):
    return render(request, 'core/complete_session.html', {'table_id': table_id})
