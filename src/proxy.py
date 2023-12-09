# import socket
# import threading
import requests
from flask import Flask, request, redirect
from consistenthashing import ConsistentHashing

app = Flask(__name__)
consistent_hashing = ConsistentHashing(['http://127.0.0.1:5001', 'http://127.0.0.1:5002'])

@app.route('/list', methods=['POST'])
def create_list():
    list_data = request.json
    server = consistent_hashing.get_server(list_data['id'])
    response = requests.post(f"{server}/list", json=list_data)
    return response.content, response.status_code


@app.route('/list/<list_id>', methods=['GET'])
def join_list(list_id):
    server = consistent_hashing.get_server(list_id)
    return redirect(f"{server}/list/{list_id}")


@app.route('/item', methods=['POST'])
def create_item():
    item_data = request.json
    server = consistent_hashing.get_server(item_data['shopping_list_id'])
    response = requests.post(f"{server}/item", json=item_data)
    return response.content, response.status_code


@app.route('/increment_item', methods=['PUT'])
def increment_quantity():
    data = request.json
    item_id = data['item_id']
    shopping_list_id = data['shopping_list_id']
    server = consistent_hashing.get_server(shopping_list_id)
    response = requests.put(f"{server}/increment_item/{item_id}")
    return response.content, response.status_code


@app.route('/decrement_item', methods=['PUT'])
def decrement_quantity():
    data = request.json
    item_id = data['item_id']
    shopping_list_id = data['shopping_list_id']
    server = consistent_hashing.get_server(shopping_list_id)
    response = requests.put(f"{server}/decrement_item/{item_id}")
    return response.content, response.status_code


@app.route('/remove_item', methods=['DELETE'])
def remove_item():
    data = request.json
    print(data)
    item_id = data['item_id']
    shopping_list_id = data['shopping_list_id']
    server = consistent_hashing.get_server(shopping_list_id)
    response = requests.delete(f"{server}/remove_item/{item_id}")
    return response.content, response.status_code

# class Proxy:
#     def __init__(self, proxy_port):
#         self.proxy_port = proxy_port
#         self.server_ring = {}
#         self.counter = 0

#     def run(self):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
#             proxy_socket.bind(('127.0.0.1', self.proxy_port))
#             proxy_socket.listen()

#             print(f"Proxy listening on port {self.proxy_port}")

#             while True:
#                 client_conn, client_addr = proxy_socket.accept()
#                 threading.Thread(target=self.handle_client, args=(client_conn,)).start()

#     def handle_client(self, client_conn):
#         data = client_conn.recv(1024).decode('utf-8')
#         if data.count(',') > 0:
#             server_id, server_port = data.split(',')
#             server_id = int(server_id)
#             server_port = int(server_port)

#             hashed_server_id = self.hash_server_id(server_id)
#             self.server_ring[hashed_server_id] = server_port
#             print(f"Server {server_id} connected on port {server_port} with hashed ID {hashed_server_id}")
#         else:
#             self.counter += 1
#             #if num:
#             #   server_id = self.get_server_for_num(int(num))
#             self.send_to_server(1, data)
#             print(f"Received number {data} from client - self.counter {self.counter}")
#             while True:
#                 num = client_conn.recv(1024).decode('utf-8') 
#                 self.counter += 1
#                 #if num:
#                  #   server_id = self.get_server_for_num(int(num))
#                 self.send_to_server(1, num)
#                 print(f"Received number {num} from client - self.counter {self.counter}")

#     def hash_server_id(self, server_id):
#         # Simple custom hash function (mod 256)
#         return server_id % 256

#     def get_server_for_num(self, num):
#         server_ids = list(self.server_ring.keys())
#         server_ids.sort()

#         hash_val = num % 256
#         return self.binary_search(server_ids, hash_val)

#     def binary_search(self, server_ids, hash_val):
#         low, high = 0, len(server_ids) - 1
#         result = None

#         while low <= high:
#             mid = (low + high) // 2
#             mid_val = server_ids[mid]

#             if mid_val >= hash_val:
#                 result = mid_val
#                 high = mid - 1
#             else:
#                 low = mid + 1

#         if result is not None:
#             return result
#         else:
#             # Wrap around if the hash_val is greater than all elements
#             return server_ids[0]

#     def send_to_server(self, server_id, num):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_conn:
#             server_conn.connect(('127.0.0.1', self.server_ring[server_id]))
#             server_conn.send(num.encode('utf-8'))
#             print(f"Sent number {num} to server {server_id}")


if __name__ == "__main__":
    # proxy_port = 8888
    # proxy = Proxy(proxy_port)
    # proxy.run()
    app.run(  "127.0.0.1", port=4000, threaded=True)
