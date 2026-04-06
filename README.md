# Data Validation API

A FastAPI-based contact validation service that verifies full names, email addresses,
and North American phone numbers. Includes a parallel stress-test client that processes 1,000+ records concurrently using asyncio and httpx.

## Live Demo

The API is deployed at `http://demo.glowingsands.ca/validate`
```bash
curl -X POST http://demo.glowingsands.ca/validate \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Doe", "email": "john@example.com", "phone_number": "123-456-7890"}'
```

## Running the Parallel Client (Using provided mock data)
Stress-tests the live API by sending 1,200 records concurrently. Results are 
printed to the console and failures written to `results/failures.csv`.
```bash
python scripts/parallel_client.py
```

## Setup

**Requirements:** Python 3.10+
```bash
git clone https://github.com/Hatem-Alfarra/data-validation-api.git
cd data-validation-api
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Server (Optional)

**Local development:**
```bash
uvicorn app.main:app --reload
```
API available at `http://127.0.0.1:8000/validate` — interactive docs at `/docs`

**Production (Linux/macOS only):**
```bash
gunicorn -c config/gunicorn.conf.py app.main:app
```
Spawns `2 * CPU cores + 1` Uvicorn workers. The live server runs this stack
behind Nginx at `http://demo.glowingsands.ca`.

## Mock Data

The CSV is included. To regenerate:
```bash
python scripts/generate_mock_data.py
```

## Running the Parallel Client (after generating own mock data)
```bash
python scripts/parallel_client.py
```

Sends 1,200 records concurrently to the API and prints a summary of valid,
invalid, and errored records with total time and throughput. Failures are
written to `results/failures.csv`.

To run against a local server, update `API_URL` at the top of
`scripts/parallel_client.py`.

## Tests
```bash
pytest tests/ -v
```

## Design Notes

**200 for invalid contacts** — an invalid contact is an expected application
outcome, not an HTTP error. FastAPI returns 422 automatically for malformed
requests.

**All errors collected simultaneously** — all three fields are validated before
returning, so clients see every problem at once rather than one at a time.

**asyncio for concurrency** — the bottleneck is network I/O.
asyncio keeps many requests in flight during network waits. Multiprocessing
would add overhead without meaningful gains at this scale.

**Semaphore at 50** — acts as a sliding window keeping exactly 50 requests in
flight. Maximizes throughput without overwhelming the server. Configurable at
the top of `parallel_client.py`.

**Single shared AsyncClient** — connection pooling eliminates repeated TCP
handshake overhead across 1,000+ requests.

**Scaling beyond 1,000 records** — the client loads the entire CSV into memory
before sending requests. For very large files this would be a memory constraint.
The solution is a producer-consumer pattern: a producer streams rows into an
asyncio queue while consumers pull from it concurrently, keeping memory usage
constant regardless of file size.

**Nginx → Gunicorn → Uvicorn** — Nginx handles the public-facing entry point
and connection buffering. Gunicorn manages worker processes. Internal traffic
stays on localhost and is never publicly exposed.