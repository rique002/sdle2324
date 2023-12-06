import socket
import threading

class Server:
    def __init__(self, server_id):
        self.server_id = server_id
        self.server_port = 1000

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
            proxy_socket.connect(('localhost', 8888))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                while True:
                    try:
                        server_socket.bind(('localhost', self.server_port))
                        break
                    except OSError:
                        self.server_port += 1
                server_socket.listen()
                proxy_socket.send(f"{self.server_id},{self.server_port}".encode('utf-8'))

                print(f"Server {self.server_id} listening on port {self.server_port}")

                while True:
                    conn, addr = server_socket.accept()
                    threading.Thread(target=self.handle_connection, args=(conn,)).start()

    def handle_connection(self, conn):
        num = conn.recv(1024).decode('utf-8')
        print(f"Received number {num} on server {self.server_id}")
        with open(f"server_{self.server_id}_output.txt", 'a') as file:
            file.write(f"{num}\n")
            file.flush()


if __name__ == "__main__":
    server_id = int(input("Enter server ID: "))
    server = Server(server_id)
    server.run()
