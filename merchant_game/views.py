from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.generic import RedirectView
from django.utils import timezone
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics

from .models import Player, City, GameData, Loan, Item
from .serializers import UserSerializer, GroupSerializer, ItemSerializer


class ItemList(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


_ROUND_DURATION = 15 * 60  # in seconds


# def _get_current_stock_prices(city):
#     elapsed_seconds = _get_elapsed_seconds()
#     current_round = _get_current_round(elapsed_seconds)
#     return CityStock.objects.filter(city=city, round=current_round)[0]


def _get_elapsed_seconds():
    now = timezone.now()
    game_start_time = GameData.objects.latest('starting_time').starting_time
    elapsed_time = now - game_start_time
    return int(elapsed_time.total_seconds())


def _get_current_round(elapsed_seconds):
    return int(elapsed_seconds/_ROUND_DURATION) + 1 if elapsed_seconds <= 6 * _ROUND_DURATION else 6


def _get_round_data():
    elapsed_seconds = _get_elapsed_seconds()
    current_round = _get_current_round(elapsed_seconds)
    seconds_remaining = _ROUND_DURATION - (elapsed_seconds % _ROUND_DURATION) if int(
        elapsed_seconds / _ROUND_DURATION) < 6 else 0
    return {"round": current_round, "time_remaining": seconds_remaining}


def index(request):
    return render(request, 'merchant_game/index.html')


@login_required(login_url='/admin/login')
def loaning(request):
    round_data = _get_round_data()
    loan = 500 + (round_data["round"] - 1) * 100
    return render(request, 'merchant_game/loaning.html', context={
        'loan': loan,
        'round_data': round_data,
    })


@login_required(login_url='/admin/login')
def lend(request):
    player = get_object_or_404(Player, code=request.POST['player'].upper())
    round_data = _get_round_data()
    previous_loans = Loan.objects.filter(player=player, round=round_data["round"])
    if len(previous_loans) > 0:
        return render(request, 'merchant_game/loaning.html', context={
            'error_message': 'Már vettél fel pénzt ebben a körben!',
            'round_data': _get_round_data(),
        })
    amount_mapping = {
        1: 500,
        2: 600,
        3: 700,
        4: 800,
        5: 900,
        6: 1000,
    }
    loan = Loan(player=player, round=round_data["round"], amount=amount_mapping[round_data["round"]])
    player.money += amount_mapping[round_data["round"]]
    player.save()
    loan.save()
    return HttpResponseRedirect(reverse('merchant_game:loaning'))


@login_required(login_url='/admin/login/')
def paying_back(request):
    loans = Loan.objects.all()
    return render(request, 'merchant_game/paying_back.html', context={
        'loans': loans,
        'round_data': _get_round_data(),
    })


@login_required(login_url='/admin/login/')
def payback(request):
    loan = get_object_or_404(Loan, pk=request.POST['loan_id'].upper())
    player = get_object_or_404(Player, code=loan.player.code)
    round_data = _get_round_data()
    player.money -= (loan.amount + ((round_data["round"] - loan.round) * int(loan.amount / 10)))
    player.save()
    loan.delete()
    return HttpResponseRedirect(reverse('merchant_game:paying-back'))


@login_required(login_url='/admin/login/')
def ending(request):
    return render(request, 'merchant_game/ending.html', context={
        'round_data': _get_round_data(),
    })


ENDING_MAPPING = [
    16,
    20,
    18,
    14,
    15,
    11,
]


@login_required(login_url='/admin/login')
def end(request):
    players = Player.objects.all()
    for player in players:
        for item_number, item_value in enumerate(ENDING_MAPPING):
            player.money += item_value * getattr(player, "item_{}_amount".format(item_number+1))
            setattr(player, "item_{}_amount".format(item_number+1), 0)
        loans = Loan.objects.filter(player=player)
        for loan in loans:
            player.money -= (loan.amount + ((6 - loan.round) * int(loan.amount / 10)))
            loan.delete()
        player.save()
    return HttpResponseRedirect(reverse('merchant_game:players'))


@login_required(login_url='/admin/login/')
def city_stock_detail(request, city):
    stock_prices = _get_current_stock_prices(city)
    return render(request, 'merchant_game/city_stock_detail.html', context={
        'city_stock': stock_prices,
        'round_data': _get_round_data(),
    })


@login_required(login_url='/admin/login/')
def trading(request, city):
    stock_prices = _get_current_stock_prices(city)
    return render(request, 'merchant_game/trading.html', context={
        'city': city,
        'city_stock': stock_prices,
        'round_data': _get_round_data(),
    })


@login_required(login_url='/admin/login/')
def trade(request, city):
    player = get_object_or_404(Player, code=request.POST['player'].upper())
    city_stock = _get_current_stock_prices(city)
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
        total_price = sell_prices[valuable] * item_amount
        if total_price > player.money:
            return render(request, 'merchant_game/trading.html', context={
                'city': city,
                'city_stock': city_stock,
                'error_message': 'Nincs ennyi pénzed!',
                'round_data': _get_round_data(),
            })
        player.money -= total_price
        setattr(player, '{}_amount'.format(valuable), player_item_mapping[valuable] + item_amount)
    else:
        if item_amount > player_item_mapping[valuable]:
            return render(request, 'merchant_game/trading.html', context={
                'city': city,
                'city_stock': city_stock,
                'error_message': 'Nincs ennyi terméked!',
                'round_data': _get_round_data(),
            })
        total_price = buy_prices[valuable] * item_amount
        player.money += total_price
        setattr(player, '{}_amount'.format(valuable), player_item_mapping[valuable] - item_amount)
    player.save()
    return HttpResponseRedirect(reverse('merchant_game:city-trading', args=(city, )))


@login_required(login_url='/admin/login/')
def bestowing(request, city=None):
    return render(request, 'merchant_game/bestowing.html', context={
        'city': city,
        'round_data': _get_round_data(),
    })


@login_required(login_url='/admin/login/')
def bestow(request, city=None):
    giver = get_object_or_404(Player, code=request.POST['giver'].upper())
    receiver = get_object_or_404(Player, code=request.POST['receiver'].upper())
    valuable = request.POST['valuable']
    amount = int(request.POST['amount'])
    if valuable == 'money':
        if amount > giver.money:
            return render(request, 'merchant_game/bestowing.html', context={
                'city': city,
                'error_message': 'Nincs ennyi pénzed!',
                'round_data': _get_round_data(),
            })
        receiver.money += amount
        giver.money -= amount
    else:
        item_amount_name = "{}_amount".format(valuable)
        if amount > getattr(giver, item_amount_name):
            return render(request, 'merchant_game/bestowing.html', context={
                'city': city,
                'error_message': 'Nincs ennyi terméked!',
                'round_data': _get_round_data(),
            })
        setattr(giver, item_amount_name, getattr(giver, item_amount_name) - amount)
        setattr(receiver, item_amount_name, getattr(receiver, item_amount_name) + amount)
    giver.save()
    receiver.save()
    return HttpResponseRedirect(reverse('merchant_game:city-bestowing', args=(city, )))


@login_required(login_url='/admin/login/')
def robbing(request, city):
    return render(request, 'merchant_game/robbing.html', context={
        'city': city,
        'round_data': _get_round_data(),
    })


@login_required(login_url='/admin/login/')
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


def player_searching(request):
    return render(request, 'merchant_game/player_searching.html')


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
