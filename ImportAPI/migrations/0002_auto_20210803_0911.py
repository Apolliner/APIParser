# Generated by Django 3.2 on 2021-08-03 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ImportAPI', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='glavbudgetclass',
            name='budget',
        ),
        migrations.AlterField(
            model_name='glavbudgetclass',
            name='code',
            field=models.CharField(max_length=3, unique=True, verbose_name='Код'),
        ),
    ]
