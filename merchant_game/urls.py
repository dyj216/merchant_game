from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'players', views.PlayerViewSet)
router.register(r'cities', views.CityViewSet)
router.register(r'loans', views.LoanViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'player-transactions', views.PlayerTransactionViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.api_root, name='api'),
    path('api/end', views.End.as_view(), name='end'),
    url(r'^api/', include(router.urls)),
]
