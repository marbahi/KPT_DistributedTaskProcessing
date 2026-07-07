# Parallel Sorting

A distributed parallel sorting system using a **Client-Master-Worker** architecture over TCP sockets. Built entirely with Python standard library — no external dependencies.

## Architecture

```
Client  ──►  Master  ──►  Worker-1
                │            Worker-2
                │            ...
                └── merges sorted chunks
```

- **Client** (`client/`) — Sends an array and sort mode to the master, waits for the final sorted result.
- **Master** (`master/`) — Accepts worker registrations, distributes data chunks, collects results, merges them, and returns the sorted array to the client.
- **Worker** (`worker/`) — Registers with the master, receives a chunk of data, sorts it locally, and sends back the sorted result.
- **Common** (`common/`) — Shared networking, configuration, and utility code.

## Usage

### 1. Start the master

```bash
python master/master.py
```

### 2. Start workers (one terminal each)

```bash
python worker/worker.py Worker-1
python worker/worker.py Worker-2
```

### 3. Run the client

```bash
python client/client.py
```

You will be prompted for:
- Input file path (JSON array or line-separated integers)
- Sort mode (`ascending` or `descending`)
- Number of workers

### Quick test

```bash
python test_integration.py
```

This starts a master, two workers, sends a sort request, and verifies correctness.

### Generate test data

```bash
python data/generate_data.py <count> <min> <max>
```

## Project structure

```
├── client/client.py
├── master/master.py          — Distributor & coordinator
├── master/merger.py          — Merge sorted chunks
├── worker/worker.py          — Sorts assigned chunks
├── common/
│   ├── communication.py      — send_json / recv_json over TCP
│   ├── config.py             — Host, port, encoding constants
│   └── utils.py              — I/O, chunking, validation
├── data/
│   ├── generate_data.py      — random data generator
│   └── input/                — sample input files
├── results/                  — sorted output directory
└── test_integration.py       — integration test
```
