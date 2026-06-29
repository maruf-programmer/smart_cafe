from django.urls import path
from core import api_views as core_api
from core import staff_api_views as staff_api
from orders import api_views as orders_api
from feedback import api_views as feedback_api

urlpatterns = [
    # Core (customer-facing)
    path('home-stats/', core_api.home_stats, name='api_home_stats'),
    path('tables/', core_api.table_list, name='api_table_list'),
    path('tables/<int:table_id>/occupy/', core_api.occupy_table, name='api_occupy_table'),
    path('tables/<int:table_id>/free/', core_api.free_table, name='api_free_table'),
    path('tables/<int:table_id>/mark-free/', core_api.mark_free, name='api_mark_free'),
    path('categories/', core_api.category_list, name='api_category_list'),
    path('menu-items/<int:item_id>/', core_api.menu_item_detail, name='api_menu_item_detail'),
    path('advertisements/', core_api.advertisement_list, name='api_advertisement_list'),
    path('waiters/', core_api.active_waiters, name='api_active_waiters'),

    # Orders (customer-facing)
    path('cart/<int:table_id>/', orders_api.get_cart, name='api_get_cart'),
    path('cart/<int:table_id>/add/', orders_api.add_to_cart, name='api_add_to_cart'),
    path('cart/<int:table_id>/remove/<int:cart_index>/', orders_api.remove_from_cart, name='api_remove_from_cart'),
    path('cart/<int:table_id>/checkout/', orders_api.checkout, name='api_checkout'),
    path('tables/<int:table_id>/orders/', orders_api.table_orders, name='api_table_orders'),
    path('orders/<int:order_id>/', orders_api.order_detail, name='api_order_detail'),
    path('orders/<int:order_id>/complete/', orders_api.complete_order_view, name='api_complete_order'),
    path('orders/<int:order_id>/payment/process/', orders_api.process_payment_api, name='api_process_payment'),
    path('waiter-calls/call/<int:table_id>/', orders_api.call_waiter_api, name='api_call_waiter'),
    path('waiter-calls/latest/<int:table_id>/', orders_api.get_latest_call, name='api_get_latest_call'),
    path('waiter-calls/active/<int:table_id>/', orders_api.get_active_calls, name='api_get_active_calls'),
    path('tables/<int:table_id>/messages/', orders_api.get_table_messages, name='api_get_table_messages'),
    path('tables/<int:table_id>/messages/send/', orders_api.send_table_message, name='api_send_table_message'),
    path('staff/messages/', orders_api.get_staff_chats, name='api_get_staff_chats'),

    # Feedback
    path('feedback/<int:table_id>/', feedback_api.submit_feedback_api, name='api_submit_feedback'),

    # Staff Admin (requires is_staff=True)
    path('staff/dashboard/', staff_api.dashboard_stats, name='api_staff_dashboard'),
    path('staff/orders/', staff_api.order_list_api, name='api_staff_orders'),
    path('staff/orders/<int:order_id>/update-status/', staff_api.update_order_status_api, name='api_update_order_status'),
    path('staff/calls/', staff_api.waiter_calls_api, name='api_staff_calls'),
    path('staff/calls/<int:call_id>/resolve/', staff_api.resolve_call_api, name='api_resolve_call'),
    path('staff/menu/', staff_api.menu_management_api, name='api_staff_menu'),
    path('staff/menu/item/add/', staff_api.menu_item_add_api, name='api_menu_item_add'),
    path('staff/menu/item/<int:item_id>/edit/', staff_api.menu_item_edit_api, name='api_menu_item_edit'),
    path('staff/menu/item/<int:item_id>/delete/', staff_api.menu_item_delete_api, name='api_menu_item_delete'),
    path('staff/upload-image/', staff_api.upload_image_api, name='api_upload_image'),
    path('staff/tables/', staff_api.table_management_api, name='api_staff_tables'),
    path('staff/tables/add/', staff_api.add_table_api, name='api_add_table'),
    path('staff/tables/<int:table_id>/status/', staff_api.update_table_status_api, name='api_update_table_status'),
    path('staff/tables/<int:table_id>/delete/', staff_api.delete_table_api, name='api_delete_table'),
    
    # API Documentation (Swagger & ReDoc)
    path('schema/', core_api.schema_view, name='api_schema'),
    path('docs/swagger/', core_api.swagger_ui_view, name='api_swagger_ui'),
    path('docs/redoc/', core_api.redoc_ui_view, name='api_redoc_ui'),
]
