# Generated by Django 3.0.6 on 2020-06-05 21:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchant_game', '0023_auto_20200605_2239'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loan',
            name='amount',
        ),
    ]
