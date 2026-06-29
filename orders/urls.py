from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('waiter/<int:table_id>/', views.call_waiter, name='call_waiter'),
    path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
]
