import csv
import json
import re
import subprocess
import threading
import time
from pathlib import Path

WORKLOADS = [
    ("W1", 1),
    ("W2", 2),
    ("W3", 4),
    ("W4", 8),
    ("W5", 16),
]

DURATION = "30s"

OUT = Path("experiment_results")
OUT.mkdir(exist_ok=True)

resource_rows = []
performance_rows = []


def monitor_resources(workload):
    start = time.time()

    while time.time() - start < 38:
        try:
            result = subprocess.run(
                [
                    "docker",
                    "stats",
                    "--no-stream",
                    "--format",
                    "{{json .}}"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.splitlines():
                if not line.strip():
                    continue

                data = json.loads(line)

                resource_rows.append({
                    "workload": workload,
                    "timestamp": time.strftime("%H:%M:%S"),
                    "container": data.get("Name", ""),
                    "cpu_percent": data.get("CPUPerc", ""),
                    "memory_usage": data.get("MemUsage", ""),
                    "memory_percent": data.get("MemPerc", "")
                })

        except Exception as e:
            print("Monitoring error:", e)

        time.sleep(1)


def run_locust(workload, users):
    command = [
        "py",
        "-m",
        "locust",
        "-f",
        "locustfile.py",
        "--headless",
        "-H",
        "http://localhost:5001",
        "-u",
        str(users),
        "-r",
        str(users),
        "-t",
        DURATION,
        "--only-summary"
    ]

    print(f"\nRunning Locust for {workload}...")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    output = result.stdout + "\n" + result.stderr

    print(output)

    # Find the aggregated statistics line.
    pattern = re.compile(
        r"GET\s+GET /students/101/dashboard\s+"
        r"(\d+)\s+"
        r"(\d+)\([^)]+\)\s+\|\s+"
        r"(\d+)\s+"
        r"(\d+)\s+"
        r"(\d+)\s+"
        r"(\d+)\s+\|\s+"
        r"([\d.]+)"
    )

    match = pattern.search(output)

    if match:
        requests = int(match.group(1))
        failures = int(match.group(2))
        average = float(match.group(3))
        minimum = int(match.group(4))
        maximum = int(match.group(5))
        median = int(match.group(6))
        rps = float(match.group(7))

        performance_rows.append({
            "workload": workload,
            "concurrent_users": users,
            "requests": requests,
            "failed": failures,
            "average_response_ms": average,
            "median_ms": median,
            "min_ms": minimum,
            "max_ms": maximum,
            "throughput_rps": rps
        })

        print(
            f"{workload}: "
            f"{requests} requests, "
            f"{failures} failures, "
            f"{average} ms average, "
            f"{rps} req/s"
        )

    else:
        print(f"WARNING: Could not parse Locust result for {workload}")


for workload, users in WORKLOADS:

    print()
    print("=" * 60)
    print(f"STARTING {workload} - {users} CONCURRENT USERS")
    print("=" * 60)

    monitor_thread = threading.Thread(
        target=monitor_resources,
        args=(workload,)
    )

    monitor_thread.start()

    run_locust(workload, users)

    monitor_thread.join()

    print(f"{workload} completed.")

    time.sleep(3)


# Save performance results
performance_file = OUT / "performance_results.csv"

with open(performance_file, "w", newline="") as f:

    fieldnames = [
        "workload",
        "concurrent_users",
        "requests",
        "failed",
        "average_response_ms",
        "median_ms",
        "min_ms",
        "max_ms",
        "throughput_rps"
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(performance_rows)


# Save resource results
resource_file = OUT / "resource_observations.csv"

with open(resource_file, "w", newline="") as f:

    fieldnames = [
        "workload",
        "timestamp",
        "container",
        "cpu_percent",
        "memory_usage",
        "memory_percent"
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(resource_rows)


print()
print("=" * 60)
print("EXPERIMENT COMPLETED")
print("=" * 60)

print(f"Performance results:")
print(performance_file)

print(f"\nResource results:")
print(resource_file)