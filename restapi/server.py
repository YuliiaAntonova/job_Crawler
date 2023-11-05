import socket


# Function to serve salary data to clients
def serve_salary_data(conn, data):
    conn.sendall(data.encode())


def main():
    host = '127.0.0.1'
    port = 50001

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")

                # Receive data from the client (you can modify this to perform different actions)
                data = conn.recv(4096).decode()

                # Send a response message to the client
                response_message = "Server received your data: " + data
                serve_salary_data(conn, response_message)


if __name__ == '__main__':
    main()
