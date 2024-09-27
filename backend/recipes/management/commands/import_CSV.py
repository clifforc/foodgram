import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def ingredients(self, csv_reader):
        for row in csv_reader:
            name, measurement_unit = row
            Ingredient.objects.create(
                name=name,
                measurement_unit=measurement_unit
            )

    def handle(self, *args, **kwargs):
        csv_file_path = '../data/ingredients.csv'
        with open(csv_file_path, 'r', encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            self.ingredients(csv_reader)
