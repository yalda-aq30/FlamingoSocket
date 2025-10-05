from django.apps import AppConfig
import threading
import os
_thread = None  #Singleton for Tread server
class MenuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'menu'

    def ready(self):
        global _thread
        #Thread just if it's main project, and did`nt create before
        def ready(self):
            start_once()
        if _thread is None and (os.environ.get("RUN_MAIN") == "true" or os.environ.get("RUN_MAIN") is None):
            from . import socket_server #We assume socket_server is in manu app
            _thread = threading.Thread(target=socket_server.start_server, daemon=True)
            _thread.start()
