import socket
from menu.models import Product, Category
from django.db import transaction
import os
import sys


#Add project direction to sys.path 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


#load django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurentproject.settings")


def start_server():
    host = '127.0.0.1'
    port = 65438  #free port for Socket server

    # making socket 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"[LISTENING] Server listening on {host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[CONNECTED] {addr} connected")

            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        print(f"[DISCONNECTED] {addr} disconnected")
                        break

                    message = data.decode().strip()
                    print(f"[RECEIVED] {message}")


                    if message.startswith("ADD_PRODUCT|"):
                        parts = message.split("|") 
                        if len(parts) == 5:
                            name = parts[1]
                            description = parts[2]
                            category_name = parts[3] 
                            price = float(parts[4]) 
                            #Make it if there is no category
                            category_obj, created = Category.objects.get_or_create(name=category_name)

                            with transaction.atomic():
                                Product.objects.create(
                                    name=name,
                                    description=description,
                                    price=price,
                                    available=True,
                                    category=category_obj   #Object is here
                                )
                            response = f"Product '{name}' added successfully in category '{category_name}'!"
                        else:
                            response = "Invalid ADD_PRODUCT format!"

                        client_socket.send(response.encode())


                        # Remove Product
                    elif message.startswith("REMOVE_PRODUCT|"):
                        print("in REMOVE_PRODUCT")
                        parts = message.split("|") 
                        if len(parts) == 2:
                            name = parts[1]
                            try:
                                with transaction.atomic():
                                    product = Product.objects.get(name=name) 
                                    product.delete()
                                response = f"Product '{name}' removed successfully!"
                            except Product.DoesNotExist:
                                response = f"Product '{name}' not found!"
                        else:
                            response = "Invalid REMOVE_PRODUCT format!"

                        client_socket.send(response.encode())


                    
                        # Get List
                    elif message == "GET_LIST":
                        products = Product.objects.all()
                        if not products.exists():
                            response = "No products available."
                        else:
                            response_lines = []
                            for p in products:
                                response_lines.append(f"{p.name} - {p.category.name} - ${p.price:.2f}")
                            response = "\n".join(response_lines)

                        client_socket.send(response.encode())
                    else: 
                        response = "Unknown command!"
                        client_socket.send(response.encode())


                except Exception as e:
                    print(f"[ERROR] {e}")
                    break

            client_socket.close()

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server stopped manually")
    finally:
        server_socket.close()
