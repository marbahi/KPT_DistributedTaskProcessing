import sys
import os
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.communication import send_json, recv_json
from common.config import HOST, MASTER_PORT
from common.utils import read_input_file


def main():
    print("=== Parallel Sorting Client ===")

    filepath = input("Input file path: ").strip()
    if not os.path.isfile(filepath):
        print(f"Error: File not found: {filepath}")
        return

    try:
        data = read_input_file(filepath)
    except ValueError as e:
        print(f"Error: {e}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    mode = input("Sort mode (ascending/descending) [ascending]: ").strip().lower()
    if mode not in ("ascending", "descending", ""):
        print("Error: Mode must be ascending or descending")
        return
    mode = mode or "ascending"

    workers_str = input("Number of workers [2]: ").strip()
    n_workers = int(workers_str) if workers_str else 2
    if n_workers < 1:
        print("Error: Number of workers must be at least 1")
        return

    print(f"\nConnecting to master at {HOST}:{MASTER_PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, MASTER_PORT))
    except ConnectionRefusedError:
        print("Error: Could not connect to master. Is it running?")
        return

    send_json(sock, {
        "type": "SORT_REQUEST",
        "mode": mode,
        "workers": n_workers,
        "data_size": len(data),
        "data": data
    })

    print("Waiting for result...")
    result = recv_json(sock)
    sock.close()

    if result is None:
        print("Error: No response from master")
        return

    if result.get("status") == "FAILED":
        print(f"Error: {result.get('message', 'Unknown error')}")
        return

    print()
    print("=== RESULT ===")
    print(f"Task ID       : {result['task_id']}")
    print(f"Status        : {result['status']}")
    print(f"Mode          : {result['mode']}")
    print(f"Workers       : {result['workers']}")
    print(f"Data size     : {result['data_size']}")
    print(f"Execution time: {result['execution_time']} seconds")
    print(f"Result        : {result['result']}")


if __name__ == "__main__":
    main()
