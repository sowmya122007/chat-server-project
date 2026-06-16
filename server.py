"""
Multi-Client Chat Server
-------------------------
Demonstrates:
  - TCP socket programming (networking)
  - Concurrency via one thread per connected client
  - Synchronization using a lock to protect shared state (the client list)
    from race conditions when multiple threads read/write it at once

Run:
    python server.py

The server listens for incoming TCP connections, spawns one thread per
connected client, and broadcasts every message it receives from a client
to all other connected clients (a classic producer-consumer / fan-out
pattern).
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 5555

# Shared state across all client threads. Because multiple threads can
# add/remove entries here at the same time (e.g. two clients connecting
# or disconnecting simultaneously), every access is wrapped in a lock.
clients_lock = threading.Lock()
clients = {}  # socket -> nickname


def broadcast(message: str, sender_socket=None) -> None:
    """Send `message` to every connected client except the sender."""
    with clients_lock:
        # Iterate over a snapshot of the keys so we can safely remove
        # dead sockets while looping without mutating the dict mid-iteration.
        for client_socket in list(clients.keys()):
            if client_socket is sender_socket:
                continue
            try:
                client_socket.sendall(message.encode("utf-8"))
            except OSError:
                _drop_locked(client_socket)


def _drop_locked(client_socket) -> None:
    """Remove a socket from `clients`. Caller must already hold clients_lock."""
    clients.pop(client_socket, None)
    try:
        client_socket.close()
    except OSError:
        pass


def remove_client(client_socket) -> None:
    with clients_lock:
        nickname = clients.pop(client_socket, None)
    if nickname:
        try:
            client_socket.close()
        except OSError:
            pass
        broadcast(f"* {nickname} has left the chat *\n")
        print(f"[DISCONNECTED] {nickname}")


def handle_client(client_socket: socket.socket, address) -> None:
    """Runs in its own thread for the lifetime of one client connection."""
    try:
        client_socket.sendall(b"Enter your nickname: ")
        nickname = client_socket.recv(1024).decode("utf-8").strip()
        if not nickname:
            nickname = f"User-{address[1]}"

        with clients_lock:
            clients[client_socket] = nickname

        print(f"[CONNECTED] {nickname} from {address}")
        broadcast(f"* {nickname} has joined the chat *\n", sender_socket=client_socket)
        client_socket.sendall(
            f"Welcome, {nickname}! Type a message and press Enter. Type /quit to leave.\n".encode("utf-8")
        )

        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # client closed the connection
            message = data.decode("utf-8").strip()
            if not message:
                continue
            print(f"[{nickname}] {message}")
            broadcast(f"[{nickname}] {message}\n", sender_socket=client_socket)

    except (ConnectionResetError, OSError):
        pass
    finally:
        remove_client(client_socket)


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, address = server_socket.accept()
            thread = threading.Thread(
                target=handle_client, args=(client_socket, address), daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        print("\n[SHUTTING DOWN]")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
