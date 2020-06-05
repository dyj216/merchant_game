from django.core import exceptions
from rest_framework import serializers

from .models import Player, City, ItemExchangeRate, ItemAmount


class ItemsField(serializers.Field):
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
                item = ItemAmount.objects.get(player=self.parent.instance, item=item_name)
            except exceptions.ObjectDoesNotExist:
                self.fail("non_existing_item", item_name=item_name)
            if amount < 0:
                self.fail("negative_value")
            item.amount = amount
            items.append(item)
        return items


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    items = ItemsField()

    class Meta:
        model = Player
        fields = ['url', 'code', 'money', 'items']

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
    class Meta:
        model = City
        fields = ['name', 'rates']
        depth = 1


class CityListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ['url', 'name']
