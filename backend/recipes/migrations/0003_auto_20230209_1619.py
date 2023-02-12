# Generated by Django 3.2.17 on 2023-02-09 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230209_1315'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='units',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(default=0, max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]