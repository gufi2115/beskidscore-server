from django.core.management.base import BaseCommand
import json
from data.helpers import teams_creator
import os

class Command(BaseCommand):
    def handle(self, *args, **options):
        current_dir = os.path.dirname(__file__)
        json_path = os.path.join(current_dir, 'matches/Klasa_B_2025_2026.json')

        with open(json_path,'r', encoding='UTF-8') as json_file:
            json_data = json.load(json_file)

        if json_data:
            teams_from_json = json_data[-1]['teams']
            teams_creator(teams_from_json)

        with open(json_path,'w', encoding='UTF-8') as json_file:
            json.dump(json_data[:-1], json_file,ensure_ascii=False, indent=4)