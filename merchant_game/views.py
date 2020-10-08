from django.core import exceptions
from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import permissions, viewsets, mixins, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .exceptions import InvalidRequestException
from .models import Player, City, GameData, Loan, Transaction, PlayerTransaction, Item, LoanPayback
from .serializers import (
    PlayerSerializer,
    PlayerListSerializer,
    CitySerializer,
    CityListSerializer,
    ItemExchangeRateSerializer,
    LoanSerializer,
    TransactionSerializer,
    PlayerTransactionSerializer, LoanPaybackSerializer,
)


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return PlayerListSerializer
        return super().get_serializer_class()

    @action(methods=['POST'], detail=True)
    def rob(self, request, *args, **kwargs):
        robber = self.get_object()
        robbed_code = request.data.get('robbed', None)
        rob_money = request.data.get('rob_money', True)

        if robbed_code is None:
            raise InvalidRequestException("robbed is required")
        if not isinstance(rob_money, bool):
            raise InvalidRequestException("rob_money should be a boolean")
        try:
            robbed = Player.objects.get(code=robbed_code)
        except exceptions.ObjectDoesNotExist as ex:
            return Response({'error': str(ex), 'robbed': robbed_code}, status=status.HTTP_404_NOT_FOUND)

        robbed_money = robbed.money if rob_money else 0
        robbed_items = robbed.items if not rob_money else {}

        return self._serialize_player_transaction(
            giver=robbed,
            taker=robber,
            money=robbed_money,
            items=robbed_items,
            request=request,
        )

    @staticmethod
    def _serialize_player_transaction(giver, taker, money, items, request):
        data = {
            'giver': giver.code,
            'taker': taker.code,
            'money': money,
            'items': items,
        }
        player_transaction = PlayerTransaction(giver=giver, taker=taker, money=money)
        player_transaction.save()
        try:
            player_transaction_serializer = PlayerTransactionSerializer(
                instance=player_transaction,
                data=data,
                context={'request': request},
            )
            if player_transaction_serializer.is_valid():
                transaction = player_transaction_serializer.save()
                return Response({
                    'status': 'Player transaction successful',
                    'player_transaction': player_transaction_serializer.to_representation(transaction),
                })
            else:
                return Response(player_transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            player_transaction.delete()
            return Response({'status': str(ex)})

    @action(methods=['POST'], detail=True)
    def gift(self, request, *args, **kwargs):
        giver = self.get_object()
        taker_code = request.data.get('taker', None)
        given_money = request.data.get('money', None)
        given_items = request.data.get('items', None)

        if taker_code is None or (given_money is None and given_items is None):
            return Response("taker and money or items are required", status=status.HTTP_400_BAD_REQUEST)
        try:
            taker = Player.objects.get(code=taker_code)
        except exceptions.ObjectDoesNotExist as ex:
            return Response({'error': str(ex), 'taker': taker_code}, status=status.HTTP_404_NOT_FOUND)

        given_money = given_money if given_money is not None else 0
        given_items = given_items if given_items is not None else {}

        try:
            self._check_gift_validity(given_money, given_items, giver)
        except InvalidRequestException as ex:
            return Response(ex.get_full_details(), status=ex.status_code)

        return self._serialize_player_transaction(
            giver=giver,
            taker=taker,
            money=given_money,
            items=given_items,
            request=request,
        )

    @staticmethod
    def _check_gift_validity(given_money, given_items, giver):
        if given_money < 0:
            raise InvalidRequestException("money shouldn't be lower than 0")
        if given_money > giver.money:
            raise InvalidRequestException("given money should be not higher than the giver's money")
        if not isinstance(given_items, dict):
            raise InvalidRequestException("items should be a dictionary of item names and amounts")
        for item_name, given_amount in given_items.items():
            giver_item_amount = giver.items.get(item_name)
            if given_amount > giver_item_amount:
                raise InvalidRequestException("given item amount should not be higher than giver's item amount")


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
    def _serialize_trade(player, amount, rate, request):
        data = {
            'player': player,
            'item_amount': amount,
            'exchange_rate': rate.id,
        }
        transaction_serializer = TransactionSerializer(data=data, context={"request": request})
        if transaction_serializer.is_valid():
            transaction = transaction_serializer.save()
            return Response({
                'status': 'Trade successful',
                'transaction': transaction_serializer.to_representation(transaction),
            })
        else:
            return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True)
    def buy(self, request, *args, **kwargs):
        try:
            player, rate, item_name, amount = self._validate_trade_data(request)
        except InvalidRequestException as ex:
            return Response(ex.get_full_details(), status=ex.status_code)
        except exceptions.ObjectDoesNotExist as ex:
            return Response({'error': str(ex)}, status=status.HTTP_404_NOT_FOUND)

        new_money = player.money - rate.buy_price * amount
        if new_money < 0:
            return Response({'error': 'Not enough money'}, status=status.HTTP_400_BAD_REQUEST)
        return self._serialize_trade(player, amount, rate, request)

    @action(methods=['POST'], detail=True)
    def sell(self, request, *args, **kwargs):
        try:
            player, rate, item_name, amount = self._validate_trade_data(request)
        except InvalidRequestException as ex:
            return Response(ex.get_full_details(), status=ex.status_code)
        except exceptions.ObjectDoesNotExist as ex:
            return Response({'error': str(ex)}, status=status.HTTP_404_NOT_FOUND)

        new_item_amount = player.items.get(item_name, 0) - amount
        if new_item_amount < 0:
            return Response({'error': 'Not enough item'}, status=status.HTTP_400_BAD_REQUEST)
        return self._serialize_trade(player, -1 * amount, rate, request)


class TransactionViewSet(
    mixins.CreateModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class PlayerTransactionViewSet(
    mixins.CreateModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = PlayerTransaction.objects.all()
    serializer_class = PlayerTransactionSerializer


class LoanViewSet(
    mixins.CreateModelMixin,
    viewsets.ReadOnlyModelViewSet
):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['POST'], detail=True)
    def pay_back_loan(self, request, *args, **kwargs):
        loan = self.get_object()
        payback = LoanPayback(loan=loan)
        if loan.player.money - payback.payback_amount < 0:
            return Response({'error': 'Not enough money'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payback.save()
        except IntegrityError:
            return Response({'error': 'This loan has been already repaid!'}, status=status.HTTP_409_CONFLICT)
        LoanPaybackSerializer(context={'request': request}).to_representation(payback)
        return Response(LoanPaybackSerializer(context={'request': request}).to_representation(payback))


class LoanPaybackViewSet(
    mixins.CreateModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = LoanPayback.objects.all()
    serializer_class = LoanPaybackSerializer
    permission_classes = [permissions.IsAuthenticated]


@permission_classes((permissions.AllowAny, ))
class End(APIView):
    def post(self, request, format=None):
        players = Player.objects.all()
        for player in players:
            for loan in player.loans.all():
                payback = LoanPayback(loan=loan)
                payback.save()
        return self.get(request, format)

    def get(self, request, format=None):
        final_prices = {item.name: item.ending_price for item in Item.objects.all()}
        result = {"final_prices": final_prices}
        game_data = GameData.objects.last()
        players = Player.objects.all()
        for player in players:
            result[player.code] = {}
            result[player.code]['money'] = player.money
            result[player.code]['final_money'] = player.money
            result[player.code]['items'] = {}
            for item_name, amount in player.items.items():
                result[player.code]['items'][item_name] = {
                    'amount': amount,
                    'value': final_prices[item_name] * amount
                }
                result[player.code]['final_money'] += result[player.code]['items'][item_name]['value']
            result[player.code]['loans'] = {}
            result[player.code]['paybacks'] = {}
            for loan in player.loans.all():
                result[player.code]['loans'][loan.round.number] = {
                    "loan_amount": loan.amount,
                }
                if hasattr(loan, 'payback'):
                    result[player.code]['paybacks'][loan.round.number] = {
                        "payback_amount": loan.payback.payback_amount,
                    }
                    result[player.code]['loans'][loan.round.number]['paid_back'] = True
                else:
                    result[player.code]['loans'][loan.round.number]['paid_back'] = False
                    result[player.code]['loans'][loan.round.number]['payback_amount'] = loan.amount + (
                            (game_data.current_round - loan.round.number) * int(
                        loan.amount * game_data.loan_interest / 100)
                    )
                    result[player.code]['final_money'] -= result[player.code]['loans'][loan.round.number]['payback_amount']
        return Response(data=result)


@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def api_root(request, format=None):
    return Response({
        'players': reverse('player-list', request=request, format=format),
        'cities': reverse('city-list', request=request, format=format),
        'loans': reverse('loan-list', request=request, format=format),
        'end': reverse('end', request=request, format=format),
    })


def index(request):
    return render(request, 'merchant_game/index.html')
