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
            return Response({'error': str(ex), 'robber': robber_code}, status=status.HTTP_404_NOT_FOUND)

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

    @action(methods=['PUT'], detail=True)
    def gift(self, request, *args, **kwargs):
        receiver = self.get_object()
        giver_code = request.data.get('giver', None)
        given_money = request.data.get('money', None)
        given_items = request.data.get('items', None)

        if giver_code is None or (given_money is None and given_items is None):
            return Response("giver and money or items are required", status=status.HTTP_400_BAD_REQUEST)
        try:
            giver = Player.objects.get(code=giver_code)
        except exceptions.ObjectDoesNotExist as ex:
            return Response({'error': str(ex), 'giver': giver_code}, status=status.HTTP_404_NOT_FOUND)

        response_dict = {
            'status': 'Gifting is successful',
            'giver': giver.code,
            'receiver': receiver.code
        }
        if given_money:
            try:
                self._gift_money(given_money, giver, receiver, response_dict)
            except InvalidRequestException as ex:
                return Response(ex.get_full_details(), status=ex.status_code)
        if given_items:
            try:
                self._gift_items(given_items, giver, receiver, response_dict)
            except InvalidRequestException as ex:
                return Response(ex.get_full_details(), status=ex.status_code)
            except exceptions.ObjectDoesNotExist as ex:
                return Response({'error': str(ex)}, status=status.HTTP_404_NOT_FOUND)

        return Response(response_dict)

    @staticmethod
    def _gift_money(given_money, giver, receiver, response_dict):
        if given_money < 0:
            raise InvalidRequestException("money shouldn't be lower than 0")
        if given_money > giver.money:
            raise InvalidRequestException("given money should be not higher than the giver's money")
        receiver.money += given_money
        giver.money -= given_money
        receiver.save()
        giver.save()
        response_dict['money'] = given_money

    @staticmethod
    def _gift_items(given_items, giver, receiver, response_dict):
        if not isinstance(given_items, dict):
            raise InvalidRequestException("items should be a dictionary of item names and amounts")
        response_dict['items'] = {}
        for item_name, given_amount in given_items.items():
            giver_item = giver.items.get(item=item_name)
            receiver_item = receiver.items.get(item=item_name)
            if given_amount > giver_item.amount:
                raise InvalidRequestException("given item amount should not be higher than giver's item amount")
            receiver_item.amount += given_amount
            giver_item.amount -= given_amount
            receiver_item.save()
            giver_item.save()
            response_dict['items'][item_name] = given_amount


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return CityListSerializer
        return super().get_serializer_class()

    @action(detail=True)
    def current_rates(self, request, *args, **kwargs):
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


def player_searching(request):
    return render(request, 'merchant_game/player_searching.html')


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
