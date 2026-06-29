from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User


def staff_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('core:staff_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            next_url = request.GET.get('next', '/staff/')
            if not next_url.startswith('/'):
                next_url = '/staff/'
            return redirect(next_url)
        else:
            messages.error(request, "Foydalanuvchi nomi yoki parol noto'g'ri, yoki sizda xodim huquqi yo'q!")
            
    return render(request, 'staff/login.html')


@staff_member_required
def staff_logout_view(request):
    auth_logout(request)
    return redirect('core:staff_login')


@staff_member_required
def staff_settings_view(request):
    user = request.user
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        
        if new_username:
            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                messages.error(request, "Xato: Ushbu foydalanuvchi nomi allaqachon band!")
            else:
                user.username = new_username
                if new_password:
                    user.set_password(new_password)
                user.save()
                auth_login(request, user)
                messages.success(request, "Profil sozlamalari muvaffaqiyatli yangilandi!")
                return redirect('core:staff_dashboard')
        else:
            messages.error(request, "Foydalanuvchi nomi bo'sh bo'lishi mumkin emas!")
            
    return render(request, 'staff/settings.html')


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
