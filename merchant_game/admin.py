from django.contrib import admin

from .models import City, Item, Player, GameData, Loan, Round, ItemAmount, ItemExchangeRate


class ItemAmountInline(admin.TabularInline):
    model = ItemAmount


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('code', 'money', 'item_amounts')
    inlines = [
        ItemAmountInline,
    ]

    @staticmethod
    def item_amounts(obj):
        item_amounts = ItemAmount.objects.filter(player=obj)
        return ", ".join(
            ("{}={}".format(item_amount.item.name, item_amount.amount) for item_amount in item_amounts)
        )


class ItemExchangeRateInline(admin.TabularInline):
    model = ItemExchangeRate
    
    
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    inlines = [
        ItemExchangeRateInline,
    ]
    
    
@admin.register(ItemAmount)
class ItemAmountAdmin(admin.ModelAdmin):
    list_display = ('player', 'item', 'amount')
    
    
@admin.register(ItemExchangeRate)
class ItemExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('city', 'round', 'buy_price', 'sell_price')
    

admin.site.register(Item)
admin.site.register(GameData)
admin.site.register(Loan)
admin.site.register(Round)
