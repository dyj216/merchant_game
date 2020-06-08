from django.core import exceptions
from django.db.models import Sum
from rest_framework import serializers

from .models import Player, City, ItemExchangeRate, Loan, Round, Transaction, PlayerTransaction, PlayerTransactionItemAmount


class PlayerTransactionItemAmountField(serializers.Field):
    default_error_messages = {
        "non_existing_item": "Item does not exist: {item_name}",
        "negative_value": "Value is too low. Ensure it is higher than 0",
    }

    def get_attribute(self, instance):
        return instance.items.all()

    def to_representation(self, value):
        return {item.item.name: item.amount for item in value}

    def to_internal_value(self, data):
        items = []
        for item_name, amount in data.items():
            try:
                item = PlayerTransactionItemAmount.objects.get(player=self.parent.instance, item=item_name)
            except exceptions.ObjectDoesNotExist:
                self.fail("non_existing_item", item_name=item_name)
            if amount < 0:
                self.fail("negative_value")
            item.amount = amount
            items.append(item)
        return items


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'url',
            'player',
            'item',
            'item_amount',
            'rate',
            'price',
            'exchange_rate'
        ]


class PlayerTransactionSerializer(serializers.ModelSerializer):
    items = PlayerTransactionItemAmountField()

    class Meta:
        model = PlayerTransaction
        fields = [
            'url',
            'giver',
            'taker',
            'money',
            'items',
        ]


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    items = serializers.SerializerMethodField()
    rob = serializers.HyperlinkedIdentityField(view_name='player-rob')
    gift = serializers.HyperlinkedIdentityField(view_name='player-gift')

    class Meta:
        model = Player
        fields = [
            'url',
            'code',
            'money',
            'items',
            'rob',
            'gift',
            'transactions',
            'giving_transactions',
            'receiving_transactions',
            'loans',
        ]

    @staticmethod
    def get_items(player):
        traded_items = {
            item['exchange_rate__item']: item['amount']
            for item
            in player.transactions.values('exchange_rate__item').annotate(amount=Sum('item_amount'))
        }
        given_items = {
            item['items__item']: item['amount']
            for item
            in player.giving_transactions.values('items__item').annotate(amount=Sum('items__amount'))
        }
        received_items = {
            item['items__item']: item['amount']
            for item
            in player.receiving_transactions.values('items__item').annotate(amount=Sum('items__amount'))
        }
        return {
            key: traded_items.get(key, 0) - given_items.get(key, 0) + received_items.get(key, 0)
            for key
            in set(traded_items) | set(given_items) | set(received_items) if key is not None
        }

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        items = validated_data.get("items", [])
        for item in items:
            item.save()
        return instance


class ItemExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemExchangeRate
        fields = ['buy_price', 'sell_price']


class CitySerializer(serializers.ModelSerializer):
    current = serializers.HyperlinkedIdentityField(view_name='city-current-rates')
    buy = serializers.HyperlinkedIdentityField(view_name='city-buy')
    sell = serializers.HyperlinkedIdentityField(view_name='city-sell')

    class Meta:
        model = City
        fields = ['name', 'current', 'buy', 'sell', 'rates']
        depth = 1


class CityListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ['url', 'name']


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['url', 'player', 'round', 'amount']
        depth = 0

    def validate(self, attrs):
        if len(Loan.objects.filter(player=attrs['player'], round=attrs['round'])):
            raise serializers.ValidationError("The player has already took a loan in the given round")
        return attrs
