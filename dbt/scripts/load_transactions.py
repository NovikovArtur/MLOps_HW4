import argparse
import base64
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4


COLUMNS = (
    "transaction_time", "merch", "cat_id", "amount", "name_1", "name_2",
    "gender", "us_state", "lat", "lon", "merchant_lat", "merchant_lon", "target",
)
NUMERIC = ("amount", "lat", "lon", "merchant_lat", "merchant_lon")


def query(sql, data=None):
    host = os.getenv("CLICKHOUSE_HOST", "localhost")
    port = os.getenv("CLICKHOUSE_PORT", "8124")
    user = os.getenv("CLICKHOUSE_USER", "hw4")
    password = os.getenv("CLICKHOUSE_PASSWORD", "hw4_local")
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    url = f"http://{host}:{port}/?{urlencode({'query': sql})}"
    request = Request(url, data=data or b"", headers={"Authorization": f"Basic {token}"})
    with urlopen(request, timeout=300) as response:
        return response.read().decode().strip()


def convert(row):
    result = {key: row[key] for key in COLUMNS}
    result["transaction_time"] = datetime.fromisoformat(row["transaction_time"]).strftime("%Y-%m-%d %H:%M:%S")
    for key in NUMERIC:
        result[key] = float(row[key])
    result["target"] = int(row["target"])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    with args.csv_file.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for statement in (root / "clickhouse/init.sql").read_text().split(";"):
            if statement.strip():
                query(statement)
        temporary = f"transactions_db.load_{uuid4().hex}"
        query(f"CREATE TABLE {temporary} AS transactions_db.transactions")
        count = 0
        batch = []
        try:
            for row in reader:
                batch.append(json.dumps(convert(row), ensure_ascii=False))
                count += 1
                if len(batch) == 10000:
                    query(f"INSERT INTO {temporary} FORMAT JSONEachRow", "\n".join(batch).encode())
                    batch.clear()
            if batch:
                query(f"INSERT INTO {temporary} FORMAT JSONEachRow", "\n".join(batch).encode())
            loaded = int(query(f"SELECT count() FROM {temporary}"))
            if not count or loaded != count:
                raise RuntimeError(f"Invalid row count: expected {count}, got {loaded}")
            query(f"EXCHANGE TABLES transactions_db.transactions AND {temporary}")
        finally:
            query(f"DROP TABLE IF EXISTS {temporary}")
    print(f"Loaded {count} rows into transactions_db.transactions")


if __name__ == "__main__":
    main()
