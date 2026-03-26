# Copilot Instructions for weakpass

This repository contains a **FastAPI backend** (`back/app`) and a **Vue-based frontend** (`qianduan`). The backend focuses on weak-password detection across several protocols. The frontend (not included here) interacts with the API under `/api/*`.

---
## High-level architecture

* **Backend (`back/app`)**
  * `main.py` – FastAPI app setup, CORS middleware, and router registration.
  * `app/api/` – routers for each public area: `auth`, `config`, `dictionary`, `detect`, `result`.
    * Each router uses FastAPI `APIRouter`; they forward requests to service functions.
  * `app/services/` – business logic. The only implemented module is `detector.py`.
    * `BaseProtocolDetector` + subclasses (`SSHDetector`, `RDPDetector`, `MySQLDetector`, `HTTPDetector`).
    * `MultiProtocolDetector` manages concurrency with an `asyncio.Semaphore`; callers pass lists of task dicts.
    * Detection functions are `async` and wrap blocking libraries with `loop.run_in_executor(...)`.
  * `app/utils/` – (empty in current tree) intended for helpers shared by services.
  * `app/core` – intended for configuration (empty currently, but `settings` imported in `main.py`).

* **Frontend (`qianduan`)**
  * Standard Vue 3 layout: `src/components`, `src/router`, `src/views`, and an `api` folder for axios wrappers.
  * Dependencies in `package.json` include `axios`, `element-plus`, `vue-router`, `echarts`, `xlsx`.
  * The UI talks to backend endpoints like `POST /api/detect/batch`.

* **Data flow**
  1. User interface triggers an AJAX call (axios) to one of the routers.
  2. Router parses and validates input, constructs a task dict.
  3. Service layer (`MultiProtocolDetector`) executes detectors concurrently.
  4. Results are returned as list of dicts with keys such as `status`, `protocol`, `ip`, `error`, `password`.

* **Extensibility**
  * To add a new protocol, subclass `BaseProtocolDetector`, implement `detect()`, and register in `MultiProtocolDetector.detectors`.
  * New router endpoints typically follow the existing pattern: prefix with `/api/<feature>` and call service functions.

---
## Developer workflows & conventions

* **Python setup**
  ```powershell
  cd back
  python -m venv venv
  .\venv\Scripts\activate
  pip install -r requirements.txt
  # optional: install extra for RDP detection on Windows
  pip install pywin32 rdpy
  ```
  Run the server during development via:
  ```powershell
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  # or simply
  python main.py
  ```
  Environment variables can be stored in a `.env` file and loaded with `python-dotenv`.

* **Frontend setup** (if code is added later)
  ```bash
  cd qianduan
  npm install
  npm run serve    # or the equivalent script in package.json
  ```
  The front-end directory currently lacks source files; treat this as a placeholder.

* **Build & packaging**
  * Backend can be bundled with `pyinstaller` using the `requirements.txt` extras. No spec file provided yet.
  * Celery/Redis are declared in requirements but not used; they are for optional asynchronous job queues.

* **Testing**
  * There are no automated tests in the workspace. Add new tests under `back/app/tests` and use `pytest` if needed.

* **Coding style**
  * Comments are Chinese; code identifiers are English.
  * Protocol names use uppercase strings (`"SSH"`, `"HTTP/HTTPS"`); task dictionaries mirror parameter names of detectors.
  * All network I/O in detectors is non-blocking to the caller via `asyncio`.

---
## Important patterns & gotchas

* `detector.MultiProtocolDetector.batch_detect` limits concurrency with a semaphore; keep `max_workers` sensible to avoid resource exhaustion.
* `HTTPDetector` uses a loose success-detection heuristic (redirects, keywords in response). When calling from routers, callers may need to supply `username_field`/`password_field` customisations.
* The `RDPDetector` will skip real checks if `pywin32`/`rdpy` are missing; routers should check `RDP_AVAILABLE` when exposing that feature.
* Most exception handling in detectors returns an error string rather than raising; downstream code should inspect `result["status"]`.

---
## Integration points & external dependencies

* **Protocol libraries** – `paramiko` (SSH), `pymysql` (MySQL), `requests` (HTTP), optionally `pywin32`/`rdpy` (RDP).
* **FastAPI** – version 0.104+; routers, middleware, async endpoints.
* **Front-end** – expects JSON responses and handles CORS using `*` origins (change for production).
* **Celery/Redis** – declared but currently unused; potential future async job handling for long-running detections.

---
## How to help an AI agent be productive

* Start by reading `back/app/main.py` and `back/app/services/detector.py` to understand the core logic.
* Routers are trivial wrappers; implement new features there (`app/api/<feature>.py`) and keep parameter names in sync with detector methods.
* Use the provided `requirements.txt` to infer required third‑party modules; filters are added manually in code comments.
* Chinese comments indicate intent and should be translated if needed (e.g. "检测异常" = detection exception).
* For any missing files (the front-end, routers, config) assume they follow the pattern shown and create them accordingly.

Please review and let me know if any sections need clarification or if I missed important project‑specific details.