# Generated by Django 3.0.2 on 2020-02-19 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartas', '0004_auto_20200219_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credito',
            name='capacidad',
            field=models.DecimalField(decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='credito',
            name='liquido',
            field=models.DecimalField(decimal_places=2, max_digits=15, null=True),
        ),
    ]
