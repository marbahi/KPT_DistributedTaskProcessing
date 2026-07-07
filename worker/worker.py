import sys
import os
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.communication import send_json, recv_json
from common.config import HOST, MASTER_PORT


def main():
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "Worker-1"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, MASTER_PORT))
    send_json(sock, {"type": "REGISTER", "worker_id": worker_id})
    print(f"[{worker_id}] Connected and registered with master")
    try:
        while True:
            msg = recv_json(sock)
            if msg is None:
                break
            if msg["type"] == "SORT_TASK":
                data = msg["data"]
                mode = msg.get("mode", "ascending")
                sorted_data = sorted(data, reverse=(mode == "descending"))
                send_json(sock, {
                    "type": "SORT_RESULT",
                    "task_id": msg["task_id"],
                    "worker_id": worker_id,
                    "status": "SUCCESS",
                    "result": sorted_data
                })
    except (ConnectionError, OSError):
        pass
    finally:
        sock.close()
        print(f"[{worker_id}] Disconnected")


if __name__ == "__main__":
    main()
