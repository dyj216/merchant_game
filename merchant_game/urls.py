
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('api/items/', views.ItemList.as_view(), name='api-item-list'),
    path('api/items/<str:pk>', views.ItemDetails.as_view(), name='api-item-details'),
    path('cities/', views.CitiesView.as_view(), name='cities'),
    path('loaning/', views.loaning, name='loaning'),
    # path('lend/', views.lend, name='lend'),
    # path('paying-back/', views.paying_back, name='paying-back'),
    # path('payback/', views.payback, name='payback'),
    # path('ending/', views.ending, name='ending'),
    # path('end/', views.end, name='end'),
    # path('bestow/', views.bestow, name='bestow'),
    # path('bestowing/', views.bestowing, name='bestowing'),
    # path('cities/<str:city>/', views.city_stock_detail, name='city-stock'),
    # path('cities/<str:city>/robbing/', views.robbing, name='city-robbing'),
    # path('cities/<str:city>/rob', views.rob, name='city-rob'),
    # path('cities/<str:city>/trading/', views.trading, name='city-trading'),
    # path('cities/<str:city>/trade', views.trade, name='city-trade'),
    # path('cities/<str:city>/bestowing/', views.bestowing, name='city-bestowing'),
    # path('cities/<str:city>/bestow/', views.bestow, name='city-bestow'),
    path('player-searching/', views.player_searching, name='player-searching'),
    # path('player-search/', views.PlayerSearchRedirectView.as_view(), name='player-search'),
    # path('players/<str:pk>/', views.PlayerView.as_view(), name='player'),
    # path('players/', views.PlayersView.as_view(), name='players'),
]
