# Generated by Django 3.0.6 on 2020-06-04 21:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchant_game', '0017_gamedata_active_round'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamedata',
            name='active_round',
        ),
    ]