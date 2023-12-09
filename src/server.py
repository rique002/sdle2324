# import socket
# import threading
# import sqlite3
import sys
from flask import Flask, request, jsonify
from models import db, ShoppingList, ShoppingItem

server_id = sys.argv[1] if len(sys.argv) > 1 else 0

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///shopping_list{server_id}.db'
db.init_app(app)


@app.route('/list', methods=['POST'])
def create_list():
    list_data = request.json
    print(list_data)
    shopping_list = ShoppingList(id=list_data['id'], name=list_data['name'])
    for item_data in list_data['items']:
        item = ShoppingItem(id=item_data['id'], name=item_data['name'], quantity=item_data['quantity'], shopping_list_id=shopping_list.id)
        db.session.add(item)
    db.session.add(shopping_list)
    db.session.commit()
    return "List created successfully", 201


@app.route('/list/<list_id>', methods=['GET'])
def get_list(list_id):
    shopping_list = ShoppingList.query.get(list_id)
    if shopping_list is None:
        return "List not found", 404
    return jsonify({'id': shopping_list.id, 'name': shopping_list.name, 'items': shopping_list.items})


@app.route('/item', methods=['POST'])
def create_item():
    item_data = request.json
    print(item_data)
    shopping_item = ShoppingItem(id=item_data['id'], name=item_data['name'], quantity=item_data['quantity'], shopping_list_id=item_data['shopping_list_id'])
    db.session.add(shopping_item)
    db.session.commit()
    return "Item created successfully", 201


@app.route('/increment_item/<string:item_id>', methods=['PUT'])
def increment_quantity(item_id):
    item = ShoppingItem.query.get(item_id)
    if item:
        new_quantity = item.quantity + 1
        item.quantity = new_quantity
        db.session.commit()
        return "Item quantity increased successfully", 204
    return "Item not found", 404


@app.route('/decrement_item/<string:item_id>', methods=['PUT'])
def decrement_quantity(item_id):
    item = ShoppingItem.query.get(item_id)
    if item and item.quantity > 0:
        new_quantity = item.quantity - 1
        item.quantity = new_quantity
        db.session.commit()
        return "Item quantity decremented successfully", 204
    return "Item not found", 404


@app.route('/remove_item/<string:item_id>', methods=['DELETE'])
def remove_item(item_id):
    item = ShoppingItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return 'Item removed successfully', 204
    return 'Item not found', 404

# class Server:
#     def __init__(self, server_id):
#         self.server_id = server_id
#         self.server_port = 1000
#         self.conn = sqlite3.connect("shopping_list"+str(server_id)+".db")  
#         self.cursor = self.conn.cursor() 
#         # Create a table for the shopping lists
#         self.cursor.execute("""
#             CREATE TABLE IF NOT EXISTS shopping_list (
#                 id INTEGER PRIMARY KEY,
#                 name TEXT NOT NULL
#             )
#         """)
#         self.conn.commit()  


#     def run(self):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
#             proxy_socket.connect(('127.0.0.1', 8888))
#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
#                 while True:
#                     try:
#                         server_socket.bind(('127.0.0.1', self.server_port))
#                         break
#                     except OSError:
#                         self.server_port += 1
#                 server_socket.listen()
#                 proxy_socket.send(f"{self.server_id},{self.server_port}".encode('utf-8'))

#                 print(f"Server {self.server_id} listening on port {self.server_port}")

#                 while True:
#                     conn, addr = server_socket.accept()
#                     threading.Thread(target=self.handle_connection, args=(conn,)).start()

#     def handle_connection(self, conn):
#         num = conn.recv(1024).decode('utf-8')
#         print(f"Received number {num} on server {self.server_id}")
#         conn_thread = sqlite3.connect("shopping_list" + str(self.server_id) + ".db")
#         cursor_thread = conn_thread.cursor()

#         cursor_thread.execute("INSERT INTO shopping_list (name) VALUES (?)", (num,))
#         conn_thread.commit()  # Commit the changes

#         with open(f"server_{self.server_id}_output.txt", 'a') as file:
#             file.write(f"{num}\n")
#             file.flush()

#         # Close the connection and cursor for this thread
#         cursor_thread.close()
#         conn_thread.close()

#     def __del__(self):
#         self.conn.close()

if __name__ == "__main__":
    #server_id = int(input("Enter server ID: "))
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host="127.0.0.1", port=5000+int(server_id), threaded=True)
