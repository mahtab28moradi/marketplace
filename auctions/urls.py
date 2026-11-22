
from django.urls import path
from . import views

urlpatterns = [
    path('<int:auction_id>/', views.auction_detail, name='auction_detail'),
    path('<int:auction_id>/bid/', views.place_bid, name='place_bid'),
    path('<int:auction_id>/result/', views.auction_result, name='auction_result'),
]
