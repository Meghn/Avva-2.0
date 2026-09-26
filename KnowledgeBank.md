# Step 1a: Initialize the project with uv

A **virtual environment** is an isolated folder of Python packages specific to one project, so installing something for Avva doesn't affect other Python projects on your machine or your system Python. `python -m venv` is the manual, built-in way to create one; you then `source .venv/bin/activate` and `pip install` into it by hand.

`uv` does the same isolation, but:

  - It creates the .venv for you automatically the first time you run uv add or uv run — no manual venv + activate step.
  - It writes a uv.lock file that pins exact versions of every dependency (and their dependencies), so the environment is perfectly reproducible on another machine or in CI.
  - It's a Rust-based tool, so installs are noticeably faster than pip.

Run this in your terminal, in the repo root:
```bash
uv init --no-readme --name avva
```
What the flags do:

`--no-readme` — skip generating a new README.md, since you already have one.
`--name avva` — names the project avva in pyproject.toml (otherwise it'd guess from the folder name Avva-2.0, which isn't a valid Python package name).
After running it, you should see a new `pyproject.toml`, a `main.py`, and a `.python-version` file.

# Step 1b: Add FastAPI and Uvicorn
- FastAPI (the framework that defines routes and validates request/response data)
- Uvicorn (the actual server process that listens on a port and runs your FastAPI app)
FastAPI describes what your API does; Uvicorn is the ASGI server that runs it, handling actual network connections. 
Nearly every Python web framework (Flask, Django, FastAPI) has this same split

Run:
```bash
uv add fastapi "uvicorn[standard]"
```
`uv add` installs the package and records it in `pyproject.toml`'s dependencies list, and writes a `uv.lock` file pinning the exact resolved versions (of these and their sub-dependencies) — this is what makes the install reproducible elsewhere.
`"uvicorn[standard]"` — the `[standard]` extra pulls in a few optional-but-common add-ons (like better performance libraries and auto-reload support), which is what most tutorials and production setups use by default.

# Step 1c: Write the actual FastAPI app with a `/health` endpoint

`/health` endpoint is one of the most common patterns in production backends — it's what load balancers, Kubernetes, Cloud Run, and uptime monitors all poll to check "is this service alive and able to respond?" before routing real traffic to it.

Create a folder `app/` with a file `app/main.py` inside it

# Step 1d: Run the server and confirm it responds

**What we're doing**: starting Uvicorn, pointing it at the `app` object we just created, and making a real HTTP request to it

**Why it matters**: this is the moment the project goes from "files on disk" to "a running service you can talk to over a network" — the same mechanism whether it's running on your laptop right now or on Cloud Run later. Getting comfortable with this loop (edit code → restart/reload → hit endpoint → check response) is the core dev cycle you'll repeat constantly

Run this in your terminal, from the repo root:

```
uv run uvicorn app.main:app --reload
```

- `uv run` — runs the command inside the project's .venv automatically, no manual activate needed.
- `uvicorn app.main:app` — tells Uvicorn where your app object lives: module path app.main (i.e. app/main.py), and the variable name app inside it.
- `--reload` — watches your files and restarts the server automatically when you save changes. Great for development; we'll turn this off in production later since it adds overhead and isn't needed once code stops changing live.

You should see log output ending in something like `Uvicorn running on http://127.0.0.1:8000`. Leave that terminal running, then open a second terminal and run:
```bash
curl http://127.0.0.1:8000/health
```
You should get back `{"status":"ok"}`

# Step 1e: Add pytest and a test client

installing `pytest` (the test runner) and `httpx` (needed because FastAPI's test client uses it to make fake HTTP requests to your app without actually starting a server on a port).

**Why it matters**: you just tested `/health` manually with `curl` — that works, but you'd have to remember to re-run it by hand every time you change anything, forever. 

An automated test does the same check in code, so it can run in under a second, get re-run every time you save, and (in Phase 8) become a required gate in CI that blocks bad code from deploying. This is the very first building block of the "eval gate" 

These are *dev* dependencies — tools needed to develop and test the project, but not needed to actually run it in production (production won't run `pytest`). `uv` has a separate flag for that distinction:

```bash
uv add --dev pytest httpx
```
- `--dev` — adds these to a separate dependency-groups.dev section in pyproject.toml instead of the main dependencies list, so production installs can skip them entirely.

# Step 1f: Write the test

Creating a `tests/` folder with one test file that spins up your FastAPI app in-memory and checks that `/health` responds correctly.

This test doesn't touch the network or a real port — it calls your app's code directly in-process, which is why it can run in milliseconds and safely in CI. The pattern here (arrange → act → assert) is the shape almost every test you'll ever write follows, no matter the framework or language.

Create `tests/test_health.py`, then run:

```bash
uv run pytest
```
You should see 1 passed.

> when pytest runs, it needs app.main to be importable.  
> But pytest only automatically adds the directory containing the test file (tests/) to Python's import path — not the repo root above it.   
> So from app.main import app fails because Python doesn't know where to look for a top-level app package.

**The fix**: tell pytest explicitly that the repo root should be on the Python path. Add this to `pyproject.toml`:
```
 [tool.pytest.ini_options]     
 (a config section pytest reads directly from)
 pythonpath = ["."].          
 (adds the current directory (repo root) to sys.path before test collection, so app.main resolves correctly no matter which directory you run pytest from)
```

> `pyproject.toml` is the single configuration file for a Python project.  
> Python projects were often a scattered mess — a `setup.py`, a `requirements.txt`, a `pytest.ini`, a `.flake8`, etc., each with its own format.    
`pyproject.toml` consolidates most of that into one file, one format (TOML), that both humans and tools can read. Later phases will add more `[tool.X]` sections here too

> The companion file, `uv.lock`, is different: `pyproject.toml` says "I need fastapi >= 0.141.1" (a range), while `uv.lock` records the exact version actually installed

---
---
