# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ubiquote.settings")
# django.setup()


import os
import sys


# 👉 chemin vers le dossier qui contient le dossier settings (donc /project-root/ubiquote)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ubiquote'))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ubiquote.settings")

import django
django.setup()

from flows import quote_ingestion_flow

if __name__ == "__main__":
    quote_ingestion_flow()
