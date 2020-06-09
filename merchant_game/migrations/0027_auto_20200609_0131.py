# Generated by Django 3.0.6 on 2020-06-08 23:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchant_game', '0026_item_ending_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money', models.BigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='PlayerTransactionItemAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.BigIntegerField(default=0)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchant_game.Item')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='merchant_game.PlayerTransaction')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_amount', models.BigIntegerField()),
                ('price', models.BigIntegerField(editable=False)),
                ('exchange_rate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='city_transactions', to='merchant_game.ItemExchangeRate')),
            ],
        ),
        migrations.RemoveField(
            model_name='player',
            name='money',
        ),
        migrations.AddField(
            model_name='loan',
            name='amount',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.DeleteModel(
            name='ItemAmount',
        ),
        migrations.AddField(
            model_name='transaction',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='merchant_game.Player'),
        ),
        migrations.AddField(
            model_name='playertransaction',
            name='giver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='giving_transactions', to='merchant_game.Player'),
        ),
        migrations.AddField(
            model_name='playertransaction',
            name='taker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiving_transactions', to='merchant_game.Player'),
        ),
    ]