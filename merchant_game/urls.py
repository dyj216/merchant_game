from django.urls import path

from . import views


app_name = 'merchant_game'
urlpatterns = [
    path('', views.index, name='index'),
    path('cities/', views.CitiesView.as_view(), name='cities'),
    path('cities/<str:city>/', views.city_stock_detail, name='city-stock'),
    path('players/', views.PlayersView.as_view(), name='players'),
    path('players/<str:pk>/', views.PlayerView.as_view(), name='player'),
    path('player-search/', views.PlayerSearchRedirectView.as_view(), name='player-search'),
]
