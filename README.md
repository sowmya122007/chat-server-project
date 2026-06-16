# Multi-Client Chat Server

A TCP chat server and client built in Python that lets multiple users
connect and message each other in real time.

## What this demonstrates

| Concept                  | Where it shows up                                                                 |
|---------------------------|------------------------------------------------------------------------------------|
| Networking / sockets      | Raw TCP sockets (`socket` module) for client-server communication                  |
| Concurrency / multi-threading | One thread per connected client on the server; a separate send/receive thread on the client |
| Synchronization            | `threading.Lock()` protects the shared `clients` dictionary from race conditions when multiple threads connect/disconnect/broadcast at the same time |
| Software design            | Clear separation between connection handling, broadcasting, and client cleanup |

## How to run it

**Terminal 1 — start the server:**
```
python server.py
```

**Terminal 2, 3, ... — start one or more clients:**
```
python client.py
```

Each client will be prompted for a nickname, then can type messages that
get broadcast to everyone else connected. Type `/quit` to disconnect.

## Why the locking matters

Without `clients_lock`, two things connecting or disconnecting at the same
moment could corrupt the shared `clients` dictionary (e.g. one thread
iterating over it to broadcast while another thread is removing an entry).
The lock ensures only one thread touches that shared state at a time —
this is the actual mechanic behind the "concurrency / synchronization"
qualification, not just a buzzword.


