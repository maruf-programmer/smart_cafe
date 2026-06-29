from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def dashboard(request):
    return render(request, 'staff/dashboard.html')


@staff_member_required
def order_list(request):
    return render(request, 'staff/orders.html')


@staff_member_required
def waiter_calls(request):
    return render(request, 'staff/calls.html')


@staff_member_required
def menu_management(request):
    return render(request, 'staff/menu.html')


@staff_member_required
def menu_item_add(request):
    return render(request, 'staff/menu_item_form.html')


@staff_member_required
def menu_item_edit(request, item_id):
    return render(request, 'staff/menu_item_form.html', {'item_id': item_id})


@staff_member_required
def table_management(request):
    return render(request, 'staff/tables.html')
