from django.urls import path

from . import views


app_name = 'merchant_game'
urlpatterns = [
    path('', views.index, name='index'),
    path('cities/', views.CitiesView.as_view(), name='cities'),
    path('cities/<str:city>/', views.city_stock_detail, name='city-stock'),
    path('cities/<str:city>/robbing/', views.robbing, name='city-robbing'),
    path('cities/<str:city>/rob', views.rob, name='city-rob'),
    path('cities/<str:city>/trading/', views.trading, name='city-trading'),
    path('cities/<str:city>/trade', views.trade, name='city-trade'),
    path('cities/<str:city>/bestowing/', views.bestowing, name='city-bestowing'),
    path('cities/<str:city>/bestow/', views.bestow, name='city-bestow'),
    path('players/', views.PlayersView.as_view(), name='players'),
    path('players/<str:pk>/', views.PlayerView.as_view(), name='player'),
    path('player-search/', views.PlayerSearchRedirectView.as_view(), name='player-search'),
]
