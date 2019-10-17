from django.db import models
from django.utils import timezone


class Item(models.Model):
    name = models.CharField(max_length=20, primary_key=True)


class Player(models.Model):
    code = models.CharField(max_length=6, primary_key=True, blank=False)
    money = models.BigIntegerField(default=1000)
    # item_1_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_2_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_3_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_4_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_5_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_6_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    item_1_amount = models.BigIntegerField(default=0)
    item_2_amount = models.BigIntegerField(default=0)
    item_3_amount = models.BigIntegerField(default=0)
    item_4_amount = models.BigIntegerField(default=0)
    item_5_amount = models.BigIntegerField(default=0)
    item_6_amount = models.BigIntegerField(default=0)


class City(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    # item_1_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_2_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_3_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_4_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_5_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_6_name = models.OneToOneField(Item, on_delete=models.CASCADE)


class CityStock(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    round = models.IntegerField()
    item_1_buy_price = models.IntegerField(blank=True, null=True,)
    item_1_sell_price = models.IntegerField(blank=True, null=True,)
    item_2_buy_price = models.IntegerField(blank=True, null=True,)
    item_2_sell_price = models.IntegerField(blank=True, null=True,)
    item_3_buy_price = models.IntegerField(blank=True, null=True,)
    item_3_sell_price = models.IntegerField(blank=True, null=True,)
    item_4_buy_price = models.IntegerField(blank=True, null=True,)
    item_4_sell_price = models.IntegerField(blank=True, null=True,)
    item_5_buy_price = models.IntegerField(blank=True, null=True,)
    item_5_sell_price = models.IntegerField(blank=True, null=True,)
    item_6_buy_price = models.IntegerField(blank=True, null=True,)
    item_6_sell_price = models.IntegerField(blank=True, null=True,)


class GameData(models.Model):
    starting_time = models.DateTimeField(default=timezone.now())
