from django.contrib import admin

from .models import City, CityStock, Item, Player, GameData


admin.site.register(City)
admin.site.register(CityStock)
admin.site.register(Item)
admin.site.register(Player)
admin.site.register(GameData)
