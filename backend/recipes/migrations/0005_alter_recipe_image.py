# Generated by Django 3.2.17 on 2023-02-15 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_ingredientrecipe_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, upload_to='recipes/images'),
        ),
    ]
