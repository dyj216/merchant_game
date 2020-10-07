from django.core.management.base import BaseCommand
from merchant_game.models import City, ItemExchangeRate, Item, Round

STOCK_DATA = {
    "Budapest": {
        1: {
            "mercury": (25, 18),
            "sulfur": (20, 15),
            "crystal": (20, 15),
            "gem": (10, 8),
            "wood": (12, 9),
            "ore": (5, 4),
        },
        2: {
            "mercury": (None, 24),
            "sulfur": (20, 18),
            "crystal": (None, 20),
            "gem": (12, 11),
            "wood": (16, 15),
            "ore": (7, 6),
        },
        3: {
            "mercury": (12, 12),
            "sulfur": (12, None),
            "crystal": (15, 14),
            "gem": (None, 16),
            "wood": (13, 12),
            "ore": (6, 6),
        },
        4: {
            "mercury": (13, 13),
            "sulfur": (12, 11),
            "crystal": (9, 8),
            "gem": (16, 15),
            "wood": (10, None),
            "ore": (10, 9),
        },
        5: {
            "mercury": (17, 15),
            "sulfur": (None, 17),
            "crystal": (12, 11),
            "gem": (17, 14),
            "wood": (15, 14),
            "ore": (10, None),
        },
        6: {
            "mercury": (22, 21),
            "sulfur": (23, 22),
            "crystal": (20, 18),
            "gem": (16, 15),
            "wood": (16, 15),
            "ore": (11, 10),
        },
    },
    "Szeged": {
        1: {
            "mercury": (15, 10),
            "sulfur": (None, 20),
            "crystal": (14, None),
            "gem": (10, 9),
            "wood": (18, 12),
            "ore": (None, 6),
        },
        2: {
            "mercury": (15, 12),
            "sulfur": (20, 18),
            "crystal": (15, 13),
            "gem": (None, 12),
            "wood": (9, None),
            "ore": (6, 6),
        },
        3: {
            "mercury": (19, 18),
            "sulfur": (15, 14),
            "crystal": (None, 21),
            "gem": (15, 14),
            "wood": (14, 12),
            "ore": (8, 7),
        },
        4: {
            "mercury": (17, 16),
            "sulfur": (None, None),
            "crystal": (8, None),
            "gem": (14, 13),
            "wood": (13, 12),
            "ore": (13, 12),
        },
        5: {
            "mercury": (None, None),
            "sulfur": (14, 12),
            "crystal": (13, 12),
            "gem": (12, 10),
            "wood": (15, 13),
            "ore": (11, 11),
        },
        6: {
            "mercury": (18, 17),
            "sulfur": (22, 22),
            "crystal": (17, 16),
            "gem": (13, 12),
            "wood": (17, 16),
            "ore": (14, 13),
        },
    },
    "Debrecen": {
        1: {
            "mercury": (20, 19),
            "sulfur": (15, None),
            "crystal": (None, 20),
            "gem": (8, None),
            "wood": (16, 14),
            "ore": (5, 3),
        },
        2: {
            "mercury": (18, 17),
            "sulfur": (12, None),
            "crystal": (9, None),
            "gem": (10, 9),
            "wood": (9, None),
            "ore": (4, 3),
        },
        3: {
            "mercury": (None, 22),
            "sulfur": (14, 13),
            "crystal": (17, 16),
            "gem": (12, 10),
            "wood": (10, 9),
            "ore": (7, 6),
        },
        4: {
            "mercury": (19, 16),
            "sulfur": (20, 19),
            "crystal": (10, 9),
            "gem": (None, 16),
            "wood": (None, 15),
            "ore": (12, 11),
        },
        5: {
            "mercury": (13, 12),
            "sulfur": (19, 17),
            "crystal": (15, 13),
            "gem": (14, 13),
            "wood": (14, 12),
            "ore": (None, None),
        },
        6: {
            "mercury": (15, 12),
            "sulfur": (16, 15),
            "crystal": (19, 18),
            "gem": (16, 15),
            "wood": (14, 14),
            "ore": (13, 12),
        },
    },
    "Sopron": {
        1: {
            "mercury": (None, 19),
            "sulfur": (None, 16),
            "crystal": (25, 19),
            "gem": (None, 10),
            "wood": (25, 20),
            "ore": (4, 3),
        },
        2: {
            "mercury": (20, 18),
            "sulfur": (24, 23),
            "crystal": (None, 18),
            "gem": (17, 16),
            "wood": (14, 13),
            "ore": (None, None),
        },
        3: {
            "mercury": (16, 14),
            "sulfur": (16, 15),
            "crystal": (18, 16),
            "gem": (15, 14),
            "wood": (21, 19),
            "ore": (None, 9),
        },
        4: {
            "mercury": (15, 14),
            "sulfur": (16, 15),
            "crystal": (11, 10),
            "gem": (17, 17),
            "wood": (15, None),
            "ore": (11, 10),
        },
        5: {
            "mercury": (17, 16),
            "sulfur": (15, None),
            "crystal": (10, None),
            "gem": (16, 16),
            "wood": (12, 12),
            "ore": (13, 12),
        },
        6: {
            "mercury": (19, 16),
            "sulfur": (17, 16),
            "crystal": (20, 20),
            "gem": (15, 15),
            "wood": (17, 16),
            "ore": (12, 11),
        },
    },
    "Eger": {
        1: {
            "mercury": (None, None),
            "sulfur": (10, 10),
            "crystal": (30, 21),
            "gem": (14, 12),
            "wood": (14, 12),
            "ore": (4, None),
        },
        2: {
            "mercury": (None, 22),
            "sulfur": (14, 13),
            "crystal": (19, 17),
            "gem": (11, 10),
            "wood": (None, 16),
            "ore": (None, 8),
        },
        3: {
            "mercury": (16, 13),
            "sulfur": (None, 22),
            "crystal": (14, 11),
            "gem": (8, 7),
            "wood": (11, 10),
            "ore": (5, 4),
        },
        4: {
            "mercury": (16, 16),
            "sulfur": (17, 16),
            "crystal": (12, 10),
            "gem": (13, 10),
            "wood": (13, 13),
            "ore": (12, 9),
        },
        5: {
            "mercury": (14, 12),
            "sulfur": (19, 17),
            "crystal": (14, 12),
            "gem": (None, None),
            "wood": (11, 10),
            "ore": (14, 13),
        },
        6: {
            "mercury": (17, 16),
            "sulfur": (25, 24),
            "crystal": (21, 20),
            "gem": (15, 15),
            "wood": (14, 12),
            "ore": (13, 10),
        },
    },
}


class Command(BaseCommand):
    help = "Populates the database with some basic data. Removes pre-existing data"

    def handle(self, *args, **options):
        ItemExchangeRate.objects.all().delete()
        City.objects.all().delete()
        Item.objects.all().delete()
        for city_name in ["Budapest", "Szeged", "Debrecen", "Sopron", "Eger"]:
            city = City(name=city_name)
            city.save()
        for item_name, ending_price in zip(
                ["mercury", "sulfur", "crystal", "gem", "wood", "ore"],
                [16, 20, 18, 14, 15, 11],
        ):
            item = Item(name=item_name, ending_price=ending_price)
            item.save()
        if Round.objects.all().count() == 0:
            for i in range(1, 7):
                r = Round()
                r.save()
        for city in City.objects.all():
            for r in Round.objects.order_by("number"):
                for item in Item.objects.all():
                    ier = ItemExchangeRate(
                        city=city,
                        round=r,
                        item=item,
                        buy_price=STOCK_DATA[city.name][r.number][item.name][0],
                        sell_price=STOCK_DATA[city.name][r.number][item.name][1],
                    )
                    ier.save()

        self.stdout.write(self.style.SUCCESS("Successfully populated tables"))
