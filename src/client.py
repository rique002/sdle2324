import socket

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 8888))

        while True:
            num = input("Enter a number: ")
            client_socket.send(num.encode('utf-8'))
            print(f"Sent number {num} to proxy")
