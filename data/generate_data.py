import sys
import json
import random
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE, "input")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    min_val = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    max_val = int(sys.argv[3]) if len(sys.argv) > 3 else n

    data = [random.randint(min_val, max_val) for _ in range(n)]

    filename = f"random_{n}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, 'w') as f:
        json.dump(data, f)

    print(f"Generated {n} integers (range {min_val}-{max_val}) → {filepath}")
    print(f"Sample: {data[:10]}...")


if __name__ == "__main__":
    main()
