from django.contrib import admin

from .models import (
    City,
    Item,
    Player,
    GameData,
    Loan,
    LoanPayback,
    Round,
    ItemExchangeRate,
    Transaction,
    PlayerTransaction,
    PlayerTransactionItemAmount,
)


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 1


class GiverTransactionInline(admin.TabularInline):
    model = PlayerTransaction
    fk_name = 'giver'
    extra = 1
    show_change_link = True


class TakerTransactionInline(admin.TabularInline):
    model = PlayerTransaction
    fk_name = 'taker'
    extra = 1
    show_change_link = True


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    inlines = [
        TransactionInline,
        GiverTransactionInline,
        TakerTransactionInline,
    ]


class ItemExchangeRateInline(admin.TabularInline):
    model = ItemExchangeRate
    extra = 1
    
    
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    inlines = [
        ItemExchangeRateInline,
    ]
    
    
@admin.register(ItemExchangeRate)
class ItemExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('city', 'round', 'buy_price', 'sell_price')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass


class PlayerTransactionItemAmountInline(admin.TabularInline):
    model = PlayerTransactionItemAmount
    extra = 1


@admin.register(PlayerTransaction)
class PlayerTransactionAdmin(admin.ModelAdmin):
    inlines = [
        PlayerTransactionItemAmountInline,
    ]


admin.site.register(Item)
admin.site.register(GameData)
admin.site.register(Loan)
admin.site.register(LoanPayback)
admin.site.register(Round)
