# Generated by Django 3.0.2 on 2020-02-20 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartas', '0005_auto_20200219_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='deuda',
            name='cantidad_pagos',
            field=models.CharField(default='0/0', max_length=100),
        ),
    ]
