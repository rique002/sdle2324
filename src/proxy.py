# import socket
# import threading
import requests
from flask import Flask, request, redirect
from consistenthashing import ConsistentHashing

app = Flask(__name__)
consistent_hashing = ConsistentHashing()

@app.route('/server', methods=['POST'])
def add_server():
    try:
        server_data = request.json
        consistent_hashing.add_server(server_data['url'])
        return "Server added successfully", 200
    except Exception as e:
        return str(e), 500

@app.route('/list', methods=['POST'])
def create_list():
    list_data = request.json
    server = consistent_hashing.get_server(list_data['id'])
    response = requests.post(f"{server}/list", json=list_data)
    return response.content, response.status_code

@app.route('/list/<string:list_id>', methods=['GET'])
def join_list(list_id):
    server = consistent_hashing.get_server(list_id)
    return redirect(f"{server}/list/{list_id}")

if __name__ == "__main__":
    # proxy_port = 8888
    # proxy = Proxy(proxy_port)
    # proxy.run()
    app.run(  "127.0.0.1", port=4000, threaded=True)
