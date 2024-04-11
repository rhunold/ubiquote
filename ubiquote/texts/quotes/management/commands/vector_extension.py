# vector_extension.py

from django.core.management.base import BaseCommand
from pgvector.django import VectorExtension

class Command(BaseCommand):
    help = 'Enable pgvector extension in the PostgreSQL database'

    def handle(self, *args, **options):
        VectorExtension().execute()
        self.stdout.write(self.style.SUCCESS('Successfully enabled pgvector extension'))
