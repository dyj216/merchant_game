# Generated by Django 3.0.6 on 2020-06-13 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchant_game', '0028_auto_20200609_2226'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanPayback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payback_amount', models.IntegerField(default=0, editable=False)),
                ('loan', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payback', to='merchant_game.Loan')),
                ('round', models.ForeignKey(editable=None, on_delete=django.db.models.deletion.CASCADE, to='merchant_game.Round')),
            ],
        ),
    ]