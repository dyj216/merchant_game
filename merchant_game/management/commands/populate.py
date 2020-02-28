from django.core.management.base import BaseCommand, CommandError
from merchant_game.models import City, CityStock, Item, Round

STOCK_DATA = {
    'Budapest': {
        1: ((25, 18), (20, 15), (20, 15), (10, 8), (12, 9), (5, 4)),
        2: ((None, 24), (20, 18), (None, 20), (12, 11), (16, 15), (7, 6)),
        3: ((12, 12), (12, None), (15, 14), (None, 16), (13, 12), (6, 6)),
        4: ((13, 13), (12, 11), (9, 8), (16, 15), (10, None), (10, 9)),
        5: ((17, 15), (None, 17), (12, 11), (17, 14), (15, 14), (10, None)),
        6: ((22, 21), (23, 22), (20, 18), (16, 15), (16, 15), (11, 10)),
    },
    'Szeged': {
        1: ((15, 10), (None, 20), (14, None), (10, 9), (18, 12), (None, 6)),
        2: ((15, 12), (20, 18), (15, 13), (None, 12), (9, None), (6, 6)),
        3: ((19, 18), (15, 14), (None, 21), (15, 14), (14, 12), (8, 7)),
        4: ((17, 16), (None, None), (8, None), (14, 13), (13, 12), (13, 12)),
        5: ((None, None), (14, 12), (13, 12), (12, 10), (15, 13), (11, 11)),
        6: ((18, 17), (22, 22), (17, 16), (13, 12), (17, 16), (14, 13)),
    },
    'Debrecen': {
        1: ((20, 19), (15, None), (None, 20), (8, None), (16, 14), (5, 3)),
        2: ((18, 17), (12, None), (9, None), (10, 9), (9, None), (4, 3)),
        3: ((None, 22), (14, 13), (17, 16), (12, 10), (10, 9), (7, 6)),
        4: ((19, 16), (20, 19), (10, 9), (None, 16), (None, 15), (12, 11)),
        5: ((13, 12), (19, 17), (15, 13), (14, 13), (14, 12), (None, None)),
        6: ((15, 12), (16, 15), (19, 18), (16, 15), (14, 14), (13, 12)),
    },
    'Sopron': {
        1: ((None, 19), (None, 16), (25, 19), (None, 10), (25, 20), (4, 3)),
        2: ((20, 18), (24, 23), (None, 18), (17, 16), (14, 13), (None, None)),
        3: ((16, 14), (16, 15), (18, 16), (15, 14), (21, 19), (None, 9)),
        4: ((15, 14), (16, 15), (11, 10), (17, 17), (15, None), (11, 10)),
        5: ((17, 16), (15, None), (10, None), (16, 16), (12, 12), (13, 12)),
        6: ((19, 16), (17, 16), (20, 20), (15, 15), (17, 16), (12, 11)),
    },
    'Eger': {
        1: ((None, None), (10, 10), (30, 21), (14, 12), (14, 12), (4, None)),
        2: ((None, 22), (14, 13), (19, 17), (11, 10), (None, 16), (None, 8)),
        3: ((16, 13), (None, 22), (14, 11), (8, 7), (11, 10), (5, 4)),
        4: ((16, 16), (17, 16), (12, 10), (13, 10), (13, 13), (12, 9)),
        5: ((14, 12), (19, 17), (14, 12), (None, None), (11, 10), (14, 13)),
        6: ((17, 16), (25, 24), (21, 20), (15, 15), (14, 12), (13, 10)),
    },
}


class Command(BaseCommand):
    help = 'Populates the database with some basic data. Removes pre-existing data'

    def handle(self, *args, **options):
        City.objects.all().delete()
        Item.objects.all().delete()
        Round.objects.all().delete()
        CityStock.objects.all().delete()
        for city_name in ['Budapest', 'Szeged', 'Debrecen', 'Sopron', 'Eger']:
            city = City(name=city_name)
            city.save()
        for item_name in ['mercury', 'sulfur', 'crystal', 'gem', 'ore', 'wood']:
            item = Item(name=item_name)
            item.save()
        for i in range(1, 7):
            r = Round()
            r.save()
        for city in City.objects.all():
            for r in Round.objects.order_by('number'):
                s = CityStock(
                    city=city,
                    round=r,
                    item_1_sell_price=STOCK_DATA[city.name][r.number][0][0],
                    item_1_buy_price=STOCK_DATA[city.name][r.number][0][1],
                    item_2_sell_price=STOCK_DATA[city.name][r.number][1][0],
                    item_2_buy_price=STOCK_DATA[city.name][r.number][1][1],
                    item_3_sell_price=STOCK_DATA[city.name][r.number][2][0],
                    item_3_buy_price=STOCK_DATA[city.name][r.number][2][1],
                    item_4_sell_price=STOCK_DATA[city.name][r.number][3][0],
                    item_4_buy_price=STOCK_DATA[city.name][r.number][3][1],
                    item_5_sell_price=STOCK_DATA[city.name][r.number][4][0],
                    item_5_buy_price=STOCK_DATA[city.name][r.number][4][1],
                    item_6_sell_price=STOCK_DATA[city.name][r.number][5][0],
                    item_6_buy_price=STOCK_DATA[city.name][r.number][5][1],
                )
                s.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated tables'))
