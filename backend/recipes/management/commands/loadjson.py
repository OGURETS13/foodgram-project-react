import os
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_file = os.path.join(settings.BASE_DIR, 'data', 'ingredients.json')
        with open(data_file) as file:
            ingredients = json.loads(file.read())
            for ingredient in ingredients:
                Ingredient.objects.create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )
        print('bolshaya pobeda')
