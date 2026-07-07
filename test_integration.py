import subprocess, time, sys, os, socket, json, signal

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from common.communication import send_json, recv_json

procs = []

def start(cmd):
    p = subprocess.Popen(cmd, cwd=BASE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append(p)
    return p

try:
    start([sys.executable, "master/master.py"])
    time.sleep(1)
    start([sys.executable, "worker/worker.py", "Worker-1"])
    start([sys.executable, "worker/worker.py", "Worker-2"])
    time.sleep(1)

    data = json.load(open("data/input/acak_100.txt"))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 5000))
    send_json(sock, {"type":"SORT_REQUEST","mode":"ascending","workers":2,"data_size":len(data),"data":data})
    result = recv_json(sock)
    sock.close()

    if result and result.get("status") == "SUCCESS":
        expected = sorted(data)
        correct = result["result"] == expected
        print(f"Status       : {result['status']}")
        print(f"Workers      : {result['workers']}")
        print(f"Data size    : {result['data_size']}")
        print(f"Exec time    : {result['execution_time']}s")
        print(f"Correctness  : {'PASS' if correct else 'FAIL'}")
    else:
        print(f"FAILED: {result}")

    # test descending
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 5000))
    send_json(sock, {"type":"SORT_REQUEST","mode":"descending","workers":2,"data_size":len(data),"data":data})
    result = recv_json(sock)
    sock.close()

    if result and result.get("status") == "SUCCESS":
        expected = sorted(data, reverse=True)
        correct = result["result"] == expected
        print(f"Descending   : {'PASS' if correct else 'FAIL'}")
    else:
        print(f"DESC FAILED: {result}")

finally:
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait()
