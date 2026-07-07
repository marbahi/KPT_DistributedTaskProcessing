import json
import struct

from common.config import ENCODING, HEADER_SIZE, BUFFER_SIZE


def send_json(sock, data):
    msg = json.dumps(data).encode(ENCODING)
    sock.sendall(struct.pack('!I', len(msg)))
    sock.sendall(msg)


def recv_json(sock):
    raw_len = sock.recv(HEADER_SIZE)
    if not raw_len:
        return None
    msg_len = struct.unpack('!I', raw_len)[0]
    chunks = []
    remaining = msg_len
    while remaining > 0:
        chunk = sock.recv(min(remaining, BUFFER_SIZE))
        if not chunk:
            raise ConnectionError("Connection broken during receive")
        chunks.append(chunk)
        remaining -= len(chunk)
    return json.loads(b''.join(chunks).decode(ENCODING))
