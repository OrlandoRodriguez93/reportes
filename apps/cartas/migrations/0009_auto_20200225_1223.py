# Generated by Django 3.0.2 on 2020-02-25 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartas', '0008_auto_20200224_1509'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plazo',
            name='cantidad_a_prestar',
        ),
        migrations.RemoveField(
            model_name='plazo',
            name='cantidad_pensionado',
        ),
        migrations.AddField(
            model_name='plazo',
            name='monto_solicitado',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='plazo',
            name='pago',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='plazo',
            name='meses_plazo',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]