import os
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BookMyShow.settings")
django.setup()

from django.core import serializers

print("Starting automatic data transfer...")
with open("complete_data.json", encoding="utf-8") as f:
    data = json.load(f)

print("Records found:", len(data))
print("Ready")
