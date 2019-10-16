from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.generic import RedirectView

from .models import Player, City, CityStock


def index(request):
    return render(request, 'merchant_game/index.html')


def city_stock_detail(request, city):
    stock_prices = CityStock.objects.filter(city=city, round=1)[0]
    return render(request, 'merchant_game/city_stock_detail.html', context={'city_stock': stock_prices})


def trading(request, city):
    stock_prices = CityStock.objects.filter(city=city, round=1)[0]
    return render(request, 'merchant_game/trading.html', context={
        'city': city,
        'city_stock': stock_prices,
    })


def trade(request, city):
    stock_prices = CityStock.objects.filter(city=city, round=1)[0]
    player = get_object_or_404(Player, code=request.POST['player'].upper())
    city_stock = CityStock.objects.filter(city=city, round=1)[0]
    exchange = request.POST['exchange']
    valuable = request.POST['valuable']
    item_amount = int(request.POST['item_amount'])
    player_item_mapping = {
        'item_1': player.item_1_amount,
        'item_2': player.item_2_amount,
        'item_3': player.item_3_amount,
        'item_4': player.item_4_amount,
        'item_5': player.item_5_amount,
        'item_6': player.item_6_amount,
    }
    buy_prices = {
        'item_1': city_stock.item_1_buy_price,
        'item_2': city_stock.item_2_buy_price,
        'item_3': city_stock.item_3_buy_price,
        'item_4': city_stock.item_4_buy_price,
        'item_5': city_stock.item_5_buy_price,
        'item_6': city_stock.item_6_buy_price,
    }
    sell_prices = {
        'item_1': city_stock.item_1_sell_price,
        'item_2': city_stock.item_2_sell_price,
        'item_3': city_stock.item_3_sell_price,
        'item_4': city_stock.item_4_sell_price,
        'item_5': city_stock.item_5_sell_price,
        'item_6': city_stock.item_6_sell_price,
    }
    if exchange == 'buy':
        total_price = buy_prices[valuable] * item_amount
        if total_price > player.money:
            return render(request, 'merchant_game/trading.html', context={
                'city': city,
                'city_stock': stock_prices,
                'error_message': 'Nincs ennyi pénzed!',
            })
        player.money -= total_price
        setattr(player, '{}_amount'.format(valuable), player_item_mapping[valuable] + item_amount)
    else:
        if item_amount > player_item_mapping[valuable]:
            return render(request, 'merchant_game/trading.html', context={
                'city': city,
                'city_stock': stock_prices,
                'error_message': 'Nincs ennyi terméked!',
            })
        total_price = sell_prices[valuable] * item_amount
        player.money += total_price
        setattr(player, '{}_amount'.format(valuable), player_item_mapping[valuable] - item_amount)
    player.save()
    return HttpResponseRedirect(reverse('merchant_game:city-trading', args=(city, )))


def robbing(request, city):
    return render(request, 'merchant_game/robbing.html', context={'city': city})


def rob(request, city):
    # robber = Player.objects.filter(name=request.POST['robber'])[0]
    robber = get_object_or_404(Player, code=request.POST['robber'].upper())
    robbed = get_object_or_404(Player, code=request.POST['robbed'].upper())
    taken_valuables = request.POST['valuables']
    if taken_valuables == 'money':
        robber.money += robbed.money
        robbed.money = 0
    else:
        robber.item_1_amount += robbed.item_1_amount
        robber.item_2_amount += robbed.item_2_amount
        robber.item_3_amount += robbed.item_3_amount
        robber.item_4_amount += robbed.item_4_amount
        robber.item_5_amount += robbed.item_5_amount
        robber.item_6_amount += robbed.item_6_amount
        robbed.item_1_amount = 0
        robbed.item_2_amount = 0
        robbed.item_3_amount = 0
        robbed.item_4_amount = 0
        robbed.item_5_amount = 0
        robbed.item_6_amount = 0
    robber.save()
    robbed.save()
    return HttpResponseRedirect(reverse('merchant_game:city-stock', args=(city, )))


class CitiesView(LoginRequiredMixin, generic.ListView):
    login_url = '/admin/login/'

    model = City
    context_object_name = 'cities'

    def get_queryset(self):
        return City.objects.all()


class PlayersView(generic.ListView):
    model = Player
    context_object_name = 'players'
    # template_name = 'merchant_game/player_list.html'

    def get_queryset(self):
        return Player.objects.all()


class PlayerView(generic.DetailView):
    model = Player


class PlayerSearchRedirectView(RedirectView):
    permanent = False
    query_string = False
    pattern_name = 'merchant_game:player'

    def get_redirect_url(self, *args, **kwargs):
        player_code = self.request.GET['pk'].upper()
        get_object_or_404(Player, pk=player_code)
        return super().get_redirect_url(*args, pk=player_code, **kwargs)
