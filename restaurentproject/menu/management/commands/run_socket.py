from django.core.management.base import BaseCommand
from menu import socket_server
import os

class Command(BaseCommand):
    help = "Run the custom socket server"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting socket server..."))

 
    