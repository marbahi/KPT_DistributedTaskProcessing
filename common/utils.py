import json


def read_input_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read().strip()
    if not content:
        raise ValueError("File kosong")
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    result = []
    for line in content.splitlines():
        line = line.strip()
        if line:
            for token in line.replace(',', ' ').split():
                result.append(int(token))
    return result


def chunk_data(data, n):
    k, m = divmod(len(data), n)
    chunks = []
    start = 0
    for i in range(n):
        size = k + (1 if i < m else 0)
        chunks.append(data[start:start + size])
        start += size
    return chunks


def validate_data(data):
    if not isinstance(data, list):
        return False, "Data harus berupa list"
    if len(data) == 0:
        return False, "Data tidak boleh kosong"
    if not all(isinstance(x, int) for x in data):
        return False, "Semua elemen harus bilangan bulat (integer)"
    return True, "OK"


def generate_task_id(index):
    return f"TASK{index:03d}"
