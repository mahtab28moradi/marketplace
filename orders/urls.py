
from django.urls import path
from . import views

urlpatterns = [
    path('buy/<int:product_id>/', views.buy_product, name='buy_product'),
    path('my-purchases/', views.my_purchases, name='my_purchases'),
]
