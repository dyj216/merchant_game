from django.contrib.auth.decorators import login_required
from django.core import exceptions
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic import RedirectView
from django.utils import timezone
from rest_framework import permissions, viewsets, mixins, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .exceptions import InvalidRequestException
from .models import Player, City, GameData, Loan, Round
from .serializers import PlayerSerializer, CitySerializer, CityListSerializer, ItemExchangeRateSerializer


class PlayerViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(methods=['PUT'], detail=True)
    def rob(self, request, *args, **kwargs):
        robbed = self.get_object()
        robber_code = request.data.get('robber', None)
        rob_money = request.data.get('rob_money', True)

        if robber_code is None:
            raise InvalidRequestException("robber is required")
        if not isinstance(rob_money, bool):
            raise InvalidRequestException("rob_money should be a boolean")
        try:
            robber = Player.objects.get(code=robber_code)
        except exceptions.ObjectDoesNotExist as ex:
            return Response({'error': str(ex)}, status=status.HTTP_404_NOT_FOUND)

        response_dict = {
            'status': 'Rob successful',
            'robber': robber.code,
            'robbed': robbed.code
        }
        if rob_money:
            robber.money += robbed.money
            response_dict['money'] = robbed.money
            robbed.money = 0
        else:
            response_dict['items'] = {}
            for robbed_item in robbed.items.exclude(amount=0):
                robber_item = robber.items.get(item=robbed_item.item.name)
                robber_item.amount += robbed_item.amount
                response_dict['items'][robber_item.item.name] = robbed_item.amount
                robbed_item.amount = 0
                robber_item.save()
                robbed_item.save()
        robber.save()
        robbed.save()

        return Response(response_dict)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return CityListSerializer
        return super().get_serializer_class()

    @action(detail=True)
    def current(self, request, *args, **kwargs):
        city = self.get_object()
        game_data = GameData.objects.last()
        response = {
            rate.item.name: ItemExchangeRateSerializer().to_representation(rate)
            for rate in city.rates.filter(round=GameData.objects.last().current_round)
        } if game_data else {}
        return Response(response)

    def _validate_trade_data(self, request):
        city = self.get_object()
        player_code = request.data.get('player', None)
        item_name = request.data.get('item', None)
        amount = request.data.get('amount', None)
        if player_code is None or item_name is None or amount is None:
            raise InvalidRequestException("player, item and amount are required")

        current_round = GameData.objects.last().current_round

        player = Player.objects.get(code=player_code)
        rate = city.rates.get(round=current_round, item=item_name)

        return player, rate, item_name, amount

    @staticmethod
    def _serialize_trade(player, data):
        player_serializer = PlayerSerializer(instance=player, data=data)
        if player_serializer.is_valid():
            player_serializer.save()
            return Response({
                'status': 'Trade successful',
                'player': data
            })
        else:
            return Response(player_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['PUT'], detail=True)
    def sell(self, request, *args, **kwargs):
        try:
            player, rate, item_name, amount = self._validate_trade_data(request)
        except InvalidRequestException as ex:
            return Response(ex.get_full_details(), status=ex.status_code)
        except exceptions.ObjectDoesNotExist as ex:
            return Response({'error': str(ex)}, status=status.HTTP_404_NOT_FOUND)

        new_money = player.money - rate.sell_price * amount
        if new_money < 0:
            return Response({'error': 'Not enough money'}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            'code': player.code,
            'money': new_money,
            'items': {
                item_name: player.items.get(item=item_name).amount + amount,
            }
        }
        return self._serialize_trade(player, data)

    @action(methods=['PUT'], detail=True)
    def buy(self, request, *args, **kwargs):
        try:
            player, rate, item_name, amount = self._validate_trade_data(request)
        except InvalidRequestException as ex:
            return Response(ex.get_full_details(), status=ex.status_code)
        except exceptions.ObjectDoesNotExist as ex:
            return Response({'error': str(ex)}, status=status.HTTP_404_NOT_FOUND)

        new_item_amount = player.items.get(item=item_name).amount - amount
        if new_item_amount < 0:
            return Response({'error': 'Not enough item'}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            'code': player.code,
            'money': player.money + rate.buy_price * amount,
            'items': {
                item_name: new_item_amount,
            }
        }
        return self._serialize_trade(player, data)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def api_root(request, format=None):
    return Response({
        'players': reverse('player-list', request=request, format=format),
        'cities': reverse('city-list', request=request, format=format),
    })


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
    game_data = GameData.objects.latest('starting_time')
    last_round = Round.objects.all().aggregate(Max('number'))['number__max']
    current_round = game_data.active_round.number
    round_duration = game_data.round_duration
    elapsed_seconds = (timezone.now() - game_data.starting_time).total_seconds()
    seconds_remaining = round_duration - (elapsed_seconds % round_duration) if int(
        elapsed_seconds / round_duration) < last_round else 0
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
    return HttpResponseRedirect(reverse('loaning'))


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
    return HttpResponseRedirect(reverse('paying-back'))


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
    return HttpResponseRedirect(reverse('players'))


@login_required(login_url='/admin/login/')
def city_stock_detail(request, city):
    stock_prices = _get_current_stock_prices(city)
    return render(request, 'merchant_game/city_stock_detail.html', context={
        'city_stock': stock_prices,
        'round_data': _get_round_data(),
    })


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
    return HttpResponseRedirect(reverse('city-bestowing', args=(city, )))


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
    return HttpResponseRedirect(reverse('city-stock', args=(city, )))


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
    pattern_name = 'player'

    def get_redirect_url(self, *args, **kwargs):
        player_code = self.request.GET['pk'].upper()
        get_object_or_404(Player, pk=player_code)
        return super().get_redirect_url(*args, pk=player_code, **kwargs)
