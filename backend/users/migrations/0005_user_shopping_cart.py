# Generated by Django 3.2.17 on 2023-02-09 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230209_1619'),
        ('users', '0004_rename_favourites_user_favorites'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='shopping_cart',
            field=models.ManyToManyField(related_name='shoppers', to='recipes.Recipe'),
        ),
    ]
