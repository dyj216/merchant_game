from django.db import models
from django.utils import timezone


class Item(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    
    def __str__(self):
        return "{}".format(self.name)


class Player(models.Model):
    code = models.CharField(max_length=6, primary_key=True, blank=False)
    money = models.BigIntegerField(default=1000)

    def __str__(self):
        return "{}".format(self.code)
    

class ItemAmount(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.BigIntegerField(default=0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["item", "player"], name="player_item"),
        ]
    
    def __str__(self):
        return "{}, {}={}".format(self.player.code, self.item.name, self.amount)


class Loan(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round = models.IntegerField()
    amount = models.IntegerField()


class City(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    
    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name


class Round(models.Model):
    number = models.AutoField(primary_key=True)
    
    def __str__(self):
        return "Round {}".format(self.number)
    
    
class ItemExchangeRate(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='rates')
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    buy_price = models.IntegerField(blank=True, null=True)
    sell_price = models.IntegerField(blank=True, null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["item", "city", "round"], name="city_item_exchange")
        ]
        
    def __str__(self):
        return (
            "{city}, round: {round}, "
            "{item} buy_price={buy_price}, sell_price={sell_price}".format(
                city=self.city.name,
                round=self.round.number,
                item=self.item.name,
                buy_price=self.buy_price,
                sell_price=self.sell_price,
            )
        )


class GameData(models.Model):
    starting_time = models.DateTimeField(default=timezone.now)
