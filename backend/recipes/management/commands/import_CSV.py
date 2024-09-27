import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from models import Ingredient

DIRECTORY = "../data/"
User = get_user_model()
NAMES_FILE = {
    "ingredients.csv": "self.ingredients(csv_reader)",
}


class Command(BaseCommand):
    help = "Import data from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def ingredients(self, csv_reader):
        for row in csv_reader:
            name, measurement_unit = row
            Ingredient.objects.create(name=name,
                                      measurement_unit=measurement_unit)

    def handle(self, *args, **kwargs):
        file_name = kwargs["csv_file"]
        csv_file_path = DIRECTORY + file_name
        with open(csv_file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            if csv_reader is not None:
                exec(NAMES_FILE[file_name])
