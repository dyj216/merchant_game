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

    def __str__(self):
        return (
            "{}, Money={}, item_1_amount={}, item_2_amount={}, item_3_amount={}, "
            "item_4_amount={}, item_5_amount={}, item_6_amount={}".format(
                self.code,
                self.money,
                self.item_1_amount,
                self.item_2_amount,
                self.item_3_amount,
                self.item_4_amount,
                self.item_5_amount,
                self.item_6_amount,
            )
        )


class Loan(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round = models.IntegerField()
    amount = models.IntegerField()


class City(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    # item_1_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_2_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_3_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_4_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_5_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_6_name = models.OneToOneField(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CityStock(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    round = models.IntegerField()
    item_1_buy_price = models.IntegerField(blank=True, null=True, )
    item_1_sell_price = models.IntegerField(blank=True, null=True, )
    item_2_buy_price = models.IntegerField(blank=True, null=True, )
    item_2_sell_price = models.IntegerField(blank=True, null=True, )
    item_3_buy_price = models.IntegerField(blank=True, null=True, )
    item_3_sell_price = models.IntegerField(blank=True, null=True, )
    item_4_buy_price = models.IntegerField(blank=True, null=True, )
    item_4_sell_price = models.IntegerField(blank=True, null=True, )
    item_5_buy_price = models.IntegerField(blank=True, null=True, )
    item_5_sell_price = models.IntegerField(blank=True, null=True, )
    item_6_buy_price = models.IntegerField(blank=True, null=True, )
    item_6_sell_price = models.IntegerField(blank=True, null=True, )

    def __str__(self):
        return (
            "{}, round={}, "
            "item_1_buy={}, item_1_sell={}, "
            "item_2_buy={}, item_2_sell={}, "
            "item_3_buy={}, item_3_sell={}, "
            "item_4_buy={}, item_4_sell={}, "
            "item_5_buy={}, item_5_sell={}, "
            "item_6_buy={}, item_6_sell={}".format(
                self.city,
                self.round,
                self.item_1_buy_price,
                self.item_1_sell_price,
                self.item_2_buy_price,
                self.item_2_sell_price,
                self.item_3_buy_price,
                self.item_3_sell_price,
                self.item_4_buy_price,
                self.item_4_sell_price,
                self.item_5_buy_price,
                self.item_5_sell_price,
                self.item_6_buy_price,
                self.item_6_sell_price,
            )
        )


class GameData(models.Model):
    starting_time = models.DateTimeField(default=timezone.now())
