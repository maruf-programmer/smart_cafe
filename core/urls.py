from django.urls import path
from . import views, admin_views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/<int:table_id>/', views.menu, name='menu'),
    path('menu/<int:table_id>/item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('cart/<int:table_id>/', views.cart, name='cart'),
    path('orders/<int:table_id>/', views.my_orders, name='my_orders'),
    path('complete/<int:table_id>/', views.complete_session, name='complete_session'),

    # Staff Admin Panel Page Routes
    path('staff/', admin_views.dashboard, name='staff_dashboard'),
    path('staff/orders/', admin_views.order_list, name='staff_orders'),
    path('staff/calls/', admin_views.waiter_calls, name='staff_calls'),
    path('staff/menu/', admin_views.menu_management, name='staff_menu'),
    path('staff/menu/item/add/', admin_views.menu_item_add, name='menu_item_add'),
    path('staff/menu/item/<int:item_id>/edit/', admin_views.menu_item_edit, name='menu_item_edit'),
    path('staff/tables/', admin_views.table_management, name='staff_tables'),
    path('api/debug/', views.debug_view, name='debug_view'),
]
