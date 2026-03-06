#!/usr/bin/env python3
"""
Simple WebSocket Client with Multiple Messages
Sends messages and waits for user responses
"""

import json
import socket
import time


def send_message():
    """Send a message and wait for response"""
    host = "localhost"
    port = 8765

    try:
        # Create socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print("Connected to server")

        # Send multiple messages
        messages = [
            "Hello from client!",
            "How are you?",
            "What's the weather like?",
            "Goodbye!",
        ]

        for message in messages:
            client_socket.send(message.encode("utf-8"))
            print(f"Sent: {message}")

            # Wait for response
            response = client_socket.recv(1024).decode("utf-8")
            data = json.loads(response)
            print(f"Received: {data['message']}")
            print("-" * 40)

            # Small delay between messages
            time.sleep(1)

        client_socket.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Simple WebSocket Client")
    print("Make sure the server is running first!")
    print("The server will ask you to type responses.")
    send_message()
