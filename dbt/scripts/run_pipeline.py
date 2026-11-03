import argparse
import subprocess
from importlib.metadata import version
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    project = root / "dbt"
    results = root / "results"
    results.mkdir(exist_ok=True)
    (results / "versions.log").write_text(
        f"dbt-core: {version('dbt-core')}\ndbt-clickhouse: {version('dbt-clickhouse')}\n"
    )
    commands = [("test", ["dbt", "test"])] if args.test_only else [
        ("deps", ["dbt", "deps"]),
        ("seed", ["dbt", "seed"]),
        ("run", ["dbt", "run"]),
        ("test", ["dbt", "test"]),
        ("docs", ["dbt", "docs", "generate", "--static"]),
    ]
    for label, command in commands:
        if label != "test":
            subprocess.run(command, cwd=project, check=True)
            continue
        with (results / "test.log").open("w") as log:
            process = subprocess.Popen(command, cwd=project, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
            result = process.wait()
        if result:
            raise SystemExit(result)


if __name__ == "__main__":
    main()
