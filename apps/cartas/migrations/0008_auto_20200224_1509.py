# Generated by Django 3.0.2 on 2020-02-24 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cartas', '0007_auto_20200220_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credito',
            name='capacidad',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='credito',
            name='id_pensionado',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='credito',
            name='id_plazo',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='credito',
            name='liquido',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='deuda',
            name='cantidad',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='deuda',
            name='cantidad_pagos',
            field=models.CharField(blank=True, default='0/0', max_length=100),
        ),
        migrations.AlterField(
            model_name='deuda',
            name='empresa',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='deuda',
            name='id_pensionado',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pensionado',
            name='ciudad',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='pensionado',
            name='direccion',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='pensionado',
            name='edad',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pensionado',
            name='estado',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='pensionado',
            name='nombre',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='pensionado',
            name='numero_social',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
