from django.db import models
from django.db.models import Max, Sum
from django.utils import timezone


class Item(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    ending_price = models.IntegerField(default=10)
    
    def __str__(self):
        return "{}".format(self.name)


class Player(models.Model):
    code = models.CharField(max_length=6, primary_key=True, blank=False)

    def __str__(self):
        return "{}".format(self.code)

    @property
    def money(self):
        money = 1000
        price_sum = self.transactions.values('price').aggregate(Sum('price'))['price__sum']
        giving_sum = self.giving_transactions.values('money').aggregate(Sum('money'))['money__sum']
        taking_sum = self.taking_transactions.values('money').aggregate(Sum('money'))['money__sum']
        loans = self.loans.values('amount').aggregate(Sum('amount'))['amount__sum']
        money += price_sum if price_sum is not None else 0
        money -= giving_sum if giving_sum is not None else 0
        money += taking_sum if taking_sum is not None else 0
        money += loans if loans is not None else 0
        return money

    @property
    def items(self):
        traded_items = {
            item['exchange_rate__item']: item['amount']
            for item
            in self.transactions.values('exchange_rate__item').annotate(amount=Sum('item_amount'))
        }
        given_items = {
            item['items__item']: item['amount']
            for item
            in self.giving_transactions.values('items__item').annotate(amount=Sum('items__amount'))
        }
        received_items = {
            item['items__item']: item['amount']
            for item
            in self.taking_transactions.values('items__item').annotate(amount=Sum('items__amount'))
        }
        return {
            key: traded_items.get(key, 0) - given_items.get(key, 0) + received_items.get(key, 0)
            for key
            in set(traded_items) | set(given_items) | set(received_items) if key is not None
        }


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
    round_duration = models.IntegerField(verbose_name="Round duration in minutes", default=15)
    starting_loan = models.IntegerField(verbose_name="Loan in the first round", default=500)
    loan_increase = models.IntegerField(verbose_name="Loan increase in each round", default=100)
    loan_interest = models.IntegerField(verbose_name="Loan interest rate (%)", default=10)

    @property
    def last_round(self):
        return Round.objects.all().aggregate(Max('number'))['number__max']

    @property
    def current_round(self):
        now = timezone.now()
        elapsed_time = int((now - self.starting_time).total_seconds())
        return (
            int(elapsed_time / self.round_duration) + 1
            if elapsed_time <= self.round_duration * self.last_round
            else self.last_round
        )


class Loan(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='loans')
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["player", "round"], name="player_loan_round")
        ]

    @property
    def get_amount(self):
        game_data = GameData.objects.last()
        return game_data.starting_loan + (self.round.number - 1) * game_data.loan_increase

    def save(self, *args, **kwargs):
        self.amount = self.get_amount
        super(Loan, self).save(*args, **kwargs)


class Transaction(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transactions')
    exchange_rate = models.ForeignKey(ItemExchangeRate, on_delete=models.CASCADE, related_name='city_transactions')
    item_amount = models.BigIntegerField()
    price = models.BigIntegerField(editable=False)

    @property
    def get_price(self):
        return -1 * self.item_amount * self.rate

    @property
    def rate(self):
        return self.exchange_rate.sell_price if self.item_amount >= 0 else self.exchange_rate.buy_price

    @property
    def item(self):
        return self.exchange_rate.item.name

    def __str__(self):
        return "'{player}' {action} {item_amount} {item} for {price} ({rate} per {item})".format(
            player=self.player.code,
            action="bought" if self.item_amount >= 0 else "sold",
            item_amount=self.item_amount,
            item=self.item,
            price=self.price,
            rate=self.rate,
        )
    
    def save(self, *args, **kwargs):
        self.price = self.get_price
        super(Transaction, self).save(*args, **kwargs)


class PlayerTransaction(models.Model):
    giver = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='giving_transactions')
    taker = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='taking_transactions')
    money = models.BigIntegerField(default=0)

    def __str__(self):
        return "'{giver}' gave '{taker}' {money} money and {items}".format(
            giver=self.giver.code,
            taker=self.taker.code,
            money=self.money,
            items={item.item.name: item.amount for item in self.items.all()}
        )


class PlayerTransactionItemAmount(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.BigIntegerField(default=0)
    transaction = models.ForeignKey(PlayerTransaction, on_delete=models.CASCADE, related_name='items')
