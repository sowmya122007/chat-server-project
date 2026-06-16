"""
Chat Client
-----------
Connects to the chat server and runs two things concurrently using threads:
  1. A background "receiver" thread that listens for incoming messages
     and prints them as soon as they arrive.
  2. The main thread, which blocks on user input and sends it to the server.

Running these on separate threads is what lets you receive a message from
another user at the same moment you're typing, without one blocking the
other.

Run (after server.py is already running):
    python client.py
"""

import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 5555


def receive_messages(sock: socket.socket) -> None:
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[Disconnected from server]")
                break
            print(data.decode("utf-8"), end="")
        except OSError:
            break


def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Could not connect to server. Is server.py running?")
        sys.exit(1)

    # Receive the nickname prompt and respond to it
    prompt = sock.recv(1024).decode("utf-8")
    print(prompt, end="")
    nickname = input()
    sock.sendall(nickname.encode("utf-8"))

    # Start a background thread for incoming messages so typing never blocks
    receiver_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    receiver_thread.start()

    try:
        while True:
            message = input()
            if message.strip().lower() == "/quit":
                break
            sock.sendall(message.encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        sock.close()


if __name__ == "__main__":
    main()
