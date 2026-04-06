import asyncio
import csv
import time
from pathlib import Path

import httpx


# Configuration

API_URL = "http://demo.glowingsands.ca/validate"
CSV_FILE = Path("scripts/mock_data.csv")
RESULTS_DIR = Path("results")
FAILURES_FILE = RESULTS_DIR / "failures.csv"

# Maximum concurrent requests. Increase for higher throughput on capable
# servers, decrease if requests are being dropped or server is overwhelmed.
MAX_CONCURRENT_REQUESTS = 50


# Core logic

async def send_request(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    row_number: int,
    data: dict,
) -> dict:
    # Using a semaphore to limit the number of concurrent requests and
    # avoid overwhelming the API or the network.
    async with semaphore:
        try:
            response = await client.post(API_URL, json=data)
            result = response.json()
            return {
                "row": row_number,
                "full_name": data["full_name"],
                "email": data["email"],
                "phone_number": data["phone_number"],
                "status": result.get("status", "unknown"),
                "errors": result.get("errors", []),
                "http_status": response.status_code,
                "exception": None,
            }
        except Exception as e:
            return {
                "row": row_number,
                "full_name": data["full_name"],
                "email": data["email"],
                "phone_number": data["phone_number"],
                "status": "error",
                "errors": [],
                "http_status": None,
                "exception": str(e),
            }


def read_csv(filepath: Path) -> list[dict]:
    with open(filepath, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_failures(failures: list[dict]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(FAILURES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["row", "full_name", "email", "phone_number", "errors"]
        )
        writer.writeheader()
        for failure in failures:
            writer.writerow({
                "row": failure["row"],
                "full_name": failure["full_name"],
                "email": failure["email"],
                "phone_number": failure["phone_number"],
                "errors": "; ".join(
                    e["message"] for e in failure["errors"]
                ),
            })


def print_summary(results: list[dict], elapsed: float) -> None:
    valid = sum(1 for r in results if r["status"] == "valid")
    invalid = sum(1 for r in results if r["status"] == "invalid")
    errors = sum(1 for r in results if r["status"] == "error")
    total = len(results)

    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total records processed : {total}")
    print(f"Valid                   : {valid}")
    print(f"Invalid                 : {invalid}")
    print(f"Request errors          : {errors}")
    print(f"Total time              : {elapsed:.2f}s")
    print(f"Throughput              : {total / elapsed:.1f} requests/sec")
    if invalid > 0:
        print(f"Failures written to     : {FAILURES_FILE}")
    print("=" * 50)


async def main() -> None:
    print(f"Reading records from {CSV_FILE}...")
    records = read_csv(CSV_FILE)
    print(f"Loaded {len(records)} records. Sending requests to {API_URL}...")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    start = time.perf_counter()
    
    # Single shared client reused across all requests. Enables connection
    # pooling eliminating repeated TCP handshake overhead.
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [
            send_request(client, semaphore, i + 1, row)
            for i, row in enumerate(records)
        ]
        # Running all tasks concurrently rather than sequentially
        results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start

    failures = [r for r in results if r["status"] in ("invalid", "error")]
    if failures:
        write_failures(failures)

    print_summary(results, elapsed)


if __name__ == "__main__":
    asyncio.run(main())