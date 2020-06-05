from django.db.models import Max
from rest_framework import serializers

from .models import Player, City, ItemExchangeRate, ItemAmount, Item


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

    def update(self, instance, validated_data):
        super().update(instance, validated_data)

        items = self.initial_data.get("items", None)
        if items:
            for item_name, amount in items.items():
                item = ItemAmount.objects.get(player=instance, item=Item.objects.get(name=item_name))
                item.amount = amount
                item.save()
        return instance


class ItemExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemExchangeRate
        fields = ['buy_price', 'sell_price']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'rates']
        depth = 1


class CityListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ['url', 'name']
