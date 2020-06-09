from rest_framework import serializers

from .models import Player, City, ItemExchangeRate, Loan, Round, Transaction, PlayerTransaction, \
    PlayerTransactionItemAmount, Item


class PlayerTransactionItemAmountField(serializers.Field):
    default_error_messages = {
        "negative_value": "Value is too low. Ensure it is higher than 0",
    }

    def get_attribute(self, instance):
        return instance.items.all()

    def to_representation(self, value):
        return {item.item.name: item.amount for item in value}

    def to_internal_value(self, data):
        items = []
        for item_name, amount in data.items():
            if amount < 0:
                self.fail("negative_value")
            item = PlayerTransactionItemAmount(
                item=Item.objects.get(name=item_name),
                transaction=self.parent.instance,
                amount=amount,
            )
            item.save()
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
            'taking_transactions',
            'loans',
        ]


class PlayerListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = [
            'url',
            'code',
            'money',
            'items',
        ]


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
