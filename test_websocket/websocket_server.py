#!/usr/bin/env python3
"""
Simple WebSocket Server with User Input
Runs continuously and allows user to input responses
"""

import json
import socket
import threading


class SimpleWebSocketServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.running = True

    def handle_client(self, client_socket, addr):
        """Handle client connection"""
        print(f"Client connected from {addr}")
        try:
            while self.running:
                # Receive message from client
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    break

                print(f"Received from client: {data}")

                # Get user input for response
                user_response = input("Enter your response: ")

                # Send user's response back to client
                response = {"message": user_response, "status": "success"}
                client_socket.send(json.dumps(response).encode("utf-8"))
                print(f"Sent to client: {user_response}")

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
            print(f"Client {addr} disconnected")

    def start_server(self):
        """Start the server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print(f"Starting server on {self.host}:{self.port}")
        print("Server running. Press Ctrl+C to stop.")
        print("When a client connects, you can type responses to send back.")

        try:
            while self.running:
                client_socket, addr = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\nServer stopping...")
            self.running = False
        finally:
            server_socket.close()


if __name__ == "__main__":
    server = SimpleWebSocketServer()
    server.start_server()
