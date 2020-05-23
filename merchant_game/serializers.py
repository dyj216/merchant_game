from django.db.models import Max
from rest_framework import serializers

from .models import Player, City, ItemExchangeRate


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ['url', 'code', 'money', 'items']

    @staticmethod
    def get_items(player):
        return {
            item.item.name: item.amount for item in player.items.all()
        }


class ItemExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemExchangeRate
        fields = ['buy_price', 'sell_price']


class CitySerializer(serializers.ModelSerializer):
    rates = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['name', 'rates']

    @staticmethod
    def get_rates(city):
        last_round = int(city.rates.all().aggregate(Max('round'))['round__max'])
        return {
            i: {
                rate.item.name: ItemExchangeRateSerializer().to_representation(rate)
                for rate in city.rates.filter(round=i)
            }
            for i in range(1, last_round + 1)
        }


class CityListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ['url', 'name']
