# Generated by Django 3.0.6 on 2020-06-05 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchant_game', '0021_auto_20200605_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='round',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchant_game.Round'),
        ),
    ]