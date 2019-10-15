from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=20, primary_key=True)


class Player(models.Model):
    code = models.CharField(max_length=6, primary_key=True, blank=False)
    money = models.IntegerField(default=1000)
    # item_1_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_2_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_3_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_4_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_5_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_6_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    item_1_amount = models.IntegerField(default=0)
    item_2_amount = models.IntegerField(default=0)
    item_3_amount = models.IntegerField(default=0)
    item_4_amount = models.IntegerField(default=0)
    item_5_amount = models.IntegerField(default=0)
    item_6_amount = models.IntegerField(default=0)
    debt = models.IntegerField(default=0)


class City(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    # item_1_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_2_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_3_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_4_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_5_name = models.OneToOneField(Item, on_delete=models.CASCADE)
    # item_6_name = models.OneToOneField(Item, on_delete=models.CASCADE)
