import sys
import os
import socket
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.communication import send_json, recv_json
from common.config import HOST, MASTER_PORT
from common.utils import chunk_data, validate_data, generate_task_id
from master.merger import merge_sorted_chunks


class MasterServer:
    def __init__(self):
        self.workers = {}
        self.workers_lock = threading.Lock()
        self.pending = {}
        self.pending_cond = threading.Condition()
        self.task_counter = 0
        self.sort_lock = threading.Lock()

    def _next_task_id(self):
        self.task_counter += 1
        return generate_task_id(self.task_counter)

    def _worker_handler(self, conn, addr, reg_msg):
        wid = reg_msg["worker_id"]
        with self.workers_lock:
            self.workers[wid] = conn
        print(f"[Master] Worker registered: {wid} ({addr})")
        try:
            while True:
                msg = recv_json(conn)
                if msg is None:
                    break
                if msg.get("type") == "SORT_RESULT":
                    tid = msg["task_id"]
                    with self.pending_cond:
                        if tid in self.pending:
                            self.pending[tid][msg["worker_id"]] = msg
                            self.pending_cond.notify_all()
        except (ConnectionError, OSError):
            pass
        finally:
            with self.workers_lock:
                self.workers.pop(wid, None)
            print(f"[Master] Worker disconnected: {wid}")
            conn.close()

    def _client_handler(self, conn, addr, req_msg):
        try:
            mode = req_msg.get("mode", "ascending")
            data = req_msg.get("data", [])
            n_workers = req_msg.get("workers", 1)

            valid, err = validate_data(data)
            if not valid:
                send_json(conn, {"type": "ERROR", "status": "FAILED", "message": err})
                return
            if mode not in ("ascending", "descending"):
                send_json(conn, {"type": "ERROR", "status": "FAILED", "message": "Mode must be ascending or descending"})
                return

            with self.workers_lock:
                available = dict(self.workers)
            if len(available) < n_workers:
                send_json(conn, {"type": "ERROR", "status": "FAILED",
                                 "message": f"Need {n_workers} workers, only {len(available)} connected"})
                return

            task_id = self._next_task_id()
            start = time.time()

            selected = list(available.items())[:n_workers]
            chunks = chunk_data(data, n_workers)

            with self.pending_cond:
                self.pending[task_id] = {}

            for i, (wid, wsock) in enumerate(selected):
                send_json(wsock, {
                    "type": "SORT_TASK",
                    "task_id": task_id,
                    "worker_id": wid,
                    "mode": mode,
                    "data": chunks[i]
                })

            with self.pending_cond:
                while len(self.pending[task_id]) < n_workers:
                    self.pending_cond.wait()
                results = self.pending.pop(task_id)

            sorted_chunks = []
            failed = False
            for wid, _ in selected:
                r = results.get(wid)
                if r and r.get("status") == "SUCCESS":
                    sorted_chunks.append(r["result"])
                else:
                    failed = True
                    send_json(conn, {"type": "ERROR", "status": "FAILED",
                                     "message": f"Worker {wid} failed"})
                    break

            if not failed:
                merged = merge_sorted_chunks(sorted_chunks, mode)
                elapsed = time.time() - start
                send_json(conn, {
                    "type": "FINAL_RESULT",
                    "task_id": task_id,
                    "status": "SUCCESS",
                    "mode": mode,
                    "workers": n_workers,
                    "data_size": len(data),
                    "execution_time": round(elapsed, 6),
                    "result": merged
                })
        except Exception as e:
            try:
                send_json(conn, {"type": "ERROR", "status": "FAILED", "message": str(e)})
            except OSError:
                pass
        finally:
            conn.close()

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, MASTER_PORT))
        server.listen()
        print(f"[Master] Listening on {HOST}:{MASTER_PORT}")
        try:
            while True:
                conn, addr = server.accept()
                msg = recv_json(conn)
                if msg is None:
                    conn.close()
                    continue
                if msg.get("type") == "REGISTER":
                    t = threading.Thread(target=self._worker_handler, args=(conn, addr, msg), daemon=True)
                    t.start()
                elif msg.get("type") == "SORT_REQUEST":
                    t = threading.Thread(target=self._client_handler, args=(conn, addr, msg), daemon=True)
                    t.start()
                else:
                    send_json(conn, {"type": "ERROR", "status": "FAILED", "message": "Unknown message type"})
                    conn.close()
        except KeyboardInterrupt:
            print("\n[Master] Shutting down...")
        finally:
            server.close()


if __name__ == "__main__":
    MasterServer().run()
