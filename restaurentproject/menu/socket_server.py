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

MAX_PRICE = 99999.0
MIN_PRICE = 0.0
MAX_MESSAGE_BYTES = 16 * 1024  # حداکثر طول پیام دریافتی

def safe_decode(data_bytes):
    try:
        return data_bytes.decode().strip()
    except Exception:
        return ""

def send_response(sock, text):
    try:
        sock.sendall(text.encode())
    except Exception:
        # در صورت بروز خطا در ارسال، چیزی نمی‌کنیم — اتصال ممکن است قطع شده باشد
        pass

def start_server():
    host = '127.0.0.1'
    port = 65438  #free port for Socket server

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[LISTENING] Server listening on {host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[CONNECTED] {addr} connected")

            while True:
                try:
                    data = client_socket.recv(MAX_MESSAGE_BYTES)
                    if not data:
                        print(f"[DISCONNECTED] {addr} disconnected")
                        break

                    message = safe_decode(data)
                    if message == "":
                        response = "ERROR: Received unreadable data."
                        print("[RECEIVED] <binary or undecodable data>")
                        send_response(client_socket, response)
                        continue

                    print(f"[RECEIVED] {message}")

                    # ADD_PRODUCT
                    if message.startswith("ADD_PRODUCT|"):
                        parts = message.split("|")
                        if len(parts) != 5:
                            response = "ERROR: Invalid ADD_PRODUCT format. Expected: ADD_PRODUCT|name|description|category|price"
                            send_response(client_socket, response)
                            continue

                        name = parts[1].strip()
                        description = parts[2].strip()
                        category_name = parts[3].strip()
                        price_raw = parts[4].strip()

                        if not name:
                            response = "ERROR: Product name cannot be empty."
                            send_response(client_socket, response)
                            continue
                        if not description:
                            response = "ERROR: Product description cannot be empty."
                            send_response(client_socket, response)
                            continue
                        if not category_name:
                            response = "ERROR: Category cannot be empty."
                            send_response(client_socket, response)
                            continue

                        try:
                            price = float(price_raw)
                        except Exception:
                            response = "ERROR: Price must be a number."
                            send_response(client_socket, response)
                            continue

                        if price < MIN_PRICE:
                            response = f"ERROR: Price cannot be negative (min {MIN_PRICE})."
                            send_response(client_socket, response)
                            continue
                        if price > MAX_PRICE:
                            response = f"ERROR: Price exceeds maximum allowed ({MAX_PRICE})."
                            send_response(client_socket, response)
                            continue

                        try:
                            category_obj, created = Category.objects.get_or_create(name=category_name)
                            with transaction.atomic():
                                Product.objects.create(
                                    name=name,
                                    description=description,
                                    price=price,
                                    available=True,
                                    category=category_obj
                                )
                            response = f"OK: Product '{name}' added successfully in category '{category_name}'!"
                        except Exception as e:
                            print(f"[ERROR] DB error on ADD_PRODUCT: {e}")
                            response = "ERROR: Internal server error while creating product."

                        send_response(client_socket, response)
                        continue

                    # REMOVE_PRODUCT
                    elif message.startswith("REMOVE_PRODUCT|"):
                        parts = message.split("|")
                        if len(parts) != 2:
                            response = "ERROR: Invalid REMOVE_PRODUCT format. Expected: REMOVE_PRODUCT|name"
                            send_response(client_socket, response)
                            continue

                        name = parts[1].strip()
                        if not name:
                            response = "ERROR: Product name cannot be empty."
                            send_response(client_socket, response)
                            continue

                        try:
                            with transaction.atomic():
                                product = Product.objects.filter(name=name).first()
                                if not product:
                                    response = f"ERROR: Product '{name}' not found."
                                else:
                                    product.delete()
                                    response = f"OK: Product '{name}' removed successfully!"
                        except Exception as e:
                            print(f"[ERROR] DB error on REMOVE_PRODUCT: {e}")
                            response = "ERROR: Internal server error while removing product."

                        send_response(client_socket, response)
                        continue

                    # GET_LIST
                    elif message == "GET_LIST" or message == "GET_PRODUCT_LIST":
                        try:
                            products = Product.objects.select_related('category').all()
                            if not products.exists():
                                response = "OK: No products available."
                            else:
                                lines = []
                                for p in products:
                                    cat_name = p.category.name if p.category else "NoCategory"
                                    # قیمت با دو رقم اعشار
                                    try:
                                        price_str = f"{p.price:.2f}"
                                    except Exception:
                                        price_str = str(p.price)
                                    lines.append(f"{p.name} - {cat_name} - ${price_str} - {p.description}")
                                response = "OK: \n" + "\n".join(lines)
                        except Exception as e:
                            print(f"[ERROR] DB error on GET_LIST: {e}")
                            response = "ERROR: Internal server error while fetching products."

                        send_response(client_socket, response)
                        continue

                    else:
                        response = "ERROR: Unknown command!"
                        send_response(client_socket, response)
                        continue

                except (ConnectionResetError, BrokenPipeError) as e:
                    print(f"[ERROR] Connection error: {e}")
                    break
                except Exception as e:
                    print(f"[ERROR] Unexpected error: {e}")
                    try:
                        send_response(client_socket, "ERROR: Unexpected server error.")
                    except Exception:
                        pass
                    # ادامه می‌دهیم تا سرور کرش نکند؛ اگر مشکل اتصال است، حلقه قطع خواهد شد
                    continue

            client_socket.close()

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server stopped manually")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
