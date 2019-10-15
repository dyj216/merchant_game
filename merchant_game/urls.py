from django.urls import path

from . import views


app_name = 'merchant_game'
urlpatterns = [
    path('', views.index, name='index'),
    path('players/', views.PlayersView.as_view(), name='players'),
    path('players/<str:pk>/', views.PlayerView.as_view(), name='player'),
    path('player-search/', views.PlayerSearchRedirectView.as_view(), name='player-search'),
]
