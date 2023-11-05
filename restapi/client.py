## client.py
import socket
from data_processing import process_data

host = '127.0.0.1'
port = 50001


def server_program():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        # Send result_df to the server
        result_df = process_data('new_combined_results.csv')
        client_socket.send(result_df.to_string(index=False).encode())

        # Receive and print the response from the server
        response = client_socket.recv(1024).decode()
        print(response)


if __name__ == '__main__':
    server_program()
