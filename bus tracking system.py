#!/usr/bin/env python3
"""
CampusRide setup script (plain text, no zip needed)

HOW TO USE
  1. Save this file as setup_campusride.py
  2. Run:   python setup_campusride.py
     It creates a folder called campusride-py with the whole project.
  3. Then:
        cd campusride-py
        python -m venv .venv
        source .venv/bin/activate        (Windows: .venv\\Scripts\\activate)
        pip install -r requirements.txt
        python -m backend.seed
        python app.py                    (open http://localhost:5000)
        python -m backend.simulate       (second terminal, makes buses move)

All project files are stored below as readable text. Each file starts with a
line like  ##### FILE: app.py #####   so you can also copy files out by hand.
"""
import os
import sys

TARGET = "campusride-py"


def main():
    if os.path.exists(TARGET):
        sys.exit("Folder '" + TARGET + "' already exists. Rename or delete it, then run again.")
    count = 0
    for block in DATA.split("\n##### FILE: ")[1:]:
        path, _, body = block.partition(" #####\n")
        body = body.rstrip("\n") + "\n"
        full = os.path.join(TARGET, *path.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        count += 1
    print("Created " + str(count) + " files in ./" + TARGET + "\n")
    print("Next steps:")
    print("  cd " + TARGET)
    print("  python -m venv .venv")
    print("  source .venv/bin/activate      (Windows: .venv\\Scripts\\activate)")
    print("  pip install -r requirements.txt")
    print("  python -m backend.seed")
    print("  python app.py                  then open http://localhost:5000")
    print("  python -m backend.simulate     (second terminal, makes buses move)")


# ------------------------------------------------------------------
# PROJECT FILES (plain text)
# ------------------------------------------------------------------
DATA = r'''
##### FILE: README.md #####
# CampusRide: college bus tracking system (Python)

Students, teachers and parents who use the college bus can see where the bus starts, every stop with its planned time, the total journey duration, and where the bus is right now. Drivers share their phone's GPS from a web page.

**Example (included as sample data):** a college in Pallavaram. The bus starts at Chennai Beach at 06:30, follows the Beach to Pallavaram local-line stations (Fort, Park, Egmore, Chetpet, Nungambakkam, Kodambakkam, Mambalam, Saidapet, Guindy, St. Thomas Mount, Pazhavanthangal, Meenambakkam, Trisulam, Pallavaram) and reaches the campus after 70 minutes.

**Stack**
- Backend: Python 3.9+ with Flask (REST API)
- Database: SQLite through Python's built-in `sqlite3` (no database server to install)
- Frontend: plain HTML, CSS and JavaScript, with Leaflet and OpenStreetMap for the map

## Who uses it

| Role | What they see |
|---|---|
| Student | Route, start point, pickup time at their stop, minutes from pickup to college, live bus ETA, a **family code** to share with parents |
| Teacher | Same as a student for their own boarding stop |
| Parent | The same trip details for each linked child (signs up with the child's email and family code) |
| Driver | Driver page that sends GPS using the bus's driver key |
| Admin | Adds routes and buses through the API |

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m backend.seed           # sample college, routes, buses, demo users
python app.py                    # http://localhost:5000
python -m backend.simulate       # second terminal: fake GPS so buses move
python -m unittest discover -s tests   # run the tests
```

Pages: `/` live map, `/login.html` sign in or sign up, `/dashboard.html` my bus, `/driver.html` driver.

Demo accounts (all passwords are `demo123`, admin is `admin123`):

| Role | Logins (add `@campus.test`) | Notes |
|---|---|---|
| Students (5) | `arun`, `priya`, `karthik`, `divya`, `rahul` | Arun boards at Guindy, Karthik at Meenambakkam, Divya at Chetpet, Priya and Rahul on the Tambaram route |
| Teachers (4) | `lakshmi`, `venkatesh`, `fathima`, `rajan` | Each boards at a different stop |
| Parents (6) | `parent` (Arun), `ramesh` and `meena` (both Karthik), `suresh` (Divya), `kavitha` (Priya and Rahul), `anitha` (Priya) | Shows two parents per child and one parent with two children |
| Admin | `admin` / `admin123` | Can add routes and buses |

Driver keys: `demo-key-A1`, `demo-key-A2`, `demo-key-B1`.

Optional settings are listed in `.env.example`. Set them as environment variables, for example `TOKEN_SECRET=... python app.py`.

## Use your own routes

Stop coordinates and timings in `backend/seed.py` are approximate samples. Edit them (the last stop of each route is the college and `minutes_from_start` is the planned time after departure), then run the seed again. Or add routes as admin:

```bash
# 1. log in as admin and copy the token
curl -X POST localhost:5000/api/auth/login -H "Content-Type: application/json" \
  -d '{"email":"admin@campus.test","password":"admin123"}'

# 2. add a route
curl -X POST localhost:5000/api/admin/routes -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" -d '{
  "name":"Velachery to College","departure_time":"07:00","return_time":"16:30",
  "stops":[
    {"name":"Velachery","lat":12.9815,"lng":80.2180,"minutes_from_start":0},
    {"name":"College Campus","lat":12.9655,"lng":80.1500,"minutes_from_start":35}]}'

# 3. add a bus for it
curl -X POST localhost:5000/api/admin/buses -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" -d '{"label":"C1","route_id":3,"driver_key":"pick-a-secret"}'
```

## API

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET | `/api/routes` | public | Routes with start, end, departure, arrival, total minutes, stops and times (`?direction=evening` for the return trip) |
| GET | `/api/routes/<id>` | public | One route |
| GET | `/api/buses` | public | Latest bus positions, online or offline |
| GET | `/api/stops/<id>/eta` | public | Minutes until each online bus reaches the stop |
| GET | `/api/buses/<id or label>/history` | public | Recent location trail |
| POST | `/api/buses/<id or label>/location` | driver | `{lat, lng, speed}` with `x-driver-key` header |
| POST | `/api/auth/register` | public | Student, teacher or parent sign up |
| POST | `/api/auth/login` | public | Returns a token (send as `Authorization: Bearer ...`) |
| GET | `/api/me` | logged in | My trip(s): pickup time, duration, live ETA |
| POST | `/api/admin/routes` | admin | Create a route with stops |
| POST | `/api/admin/buses` | admin | Create a bus |

## Project structure

```
app.py               Flask app: all API routes, serves the front end
backend/
  db.py              SQLite connection and table definitions
  service.py         Schedules, durations, ETA, sign up and login logic
  auth.py            Password hashing, signed tokens, role checks
  seed.py            Sample college, routes and users
  simulate.py        Fake GPS for demos
public/              HTML, CSS and JS front end (map, login, dashboard, driver)
tests/test_app.py    API tests
requirements.txt
```

## Database

`routes` (with `departure_time` and `return_time`) → `stops` (ordered, with `minutes_from_start`); `routes` → `buses` → `location_history`; `users` (role, route, boarding stop, family code) and `parent_children` linking parents to students. Tables are created automatically on first run.

## Known limits and next steps

- Times on the dashboard are the **planned** schedule. Live ETA is straight-line distance divided by average speed, so it ignores roads and does not know whether the bus has already passed your stop.
- The pages refresh every few seconds. WebSockets would make updates instant.
- Before real use: set a strong `TOKEN_SECRET`, change every demo password and driver key, serve over HTTPS (phones only share location on HTTPS), and run behind a production server such as `gunicorn app:app` instead of the Flask development server.
- Ideas: push or SMS alerts when the bus is near, delay notices, attendance, an admin web page, PostgreSQL for large colleges.

## Push to GitHub

```bash
git init
git add .
git commit -m "CampusRide: college bus tracking system (Flask + SQLite)"
git branch -M main
git remote add origin https://github.com/<your-username>/campusride.git
git push -u origin main
```

## License

MIT

##### FILE: .env.example #####
PORT=5000
# Secret used to sign login tokens. Set a long random value in production.
TOKEN_SECRET=change-me-to-a-long-random-string
# Buses that have not reported in this many seconds are shown as offline
STALE_SECONDS=60
# Average bus speed (km/h) used for ETA estimates
AVG_SPEED_KMH=20

##### FILE: .gitignore #####
__pycache__/
*.pyc
.venv/
venv/
*.db
*.db-shm
*.db-wal
.env
.DS_Store

##### FILE: app.py #####
"""CampusRide backend: Flask REST API + serves the HTML/CSS/JS front end from ./public.
Run: python app.py   then open http://localhost:5000"""
import os

from flask import Flask, g, jsonify, request, send_from_directory

from backend import service as svc
from backend.auth import require_auth
from backend.errors import HttpError

ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(ROOT, "public"), static_url_path="")


@app.errorhandler(HttpError)
def on_http_error(e):
    return jsonify(error=e.message), e.status


@app.errorhandler(404)
def on_404(e):
    return jsonify(error="Not found"), 404


def body():
    return request.get_json(silent=True) or {}


def direction():
    return "evening" if request.args.get("direction") == "evening" else "morning"


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# ----- Public: routes, schedules, live buses -----

@app.get("/api/routes")
def routes():
    """All routes with start point, end point, total duration and stops with scheduled times.
    ?direction=evening gives the return trip (college back to first stop)."""
    return jsonify(svc.list_routes(direction()))


@app.get("/api/routes/<int:route_id>")
def route(route_id):
    r = svc.route_detail(route_id, direction())
    if not r:
        raise HttpError(404, "Route not found")
    return jsonify(r)


@app.get("/api/buses")
def buses():
    return jsonify(svc.list_buses(request.args.get("route_id", type=int)))


@app.get("/api/stops/<int:stop_id>/eta")
def stop_eta(stop_id):
    return jsonify(svc.stop_eta(stop_id))


@app.get("/api/buses/<bus_ref>/history")
def history(bus_ref):
    return jsonify(svc.bus_history(bus_ref, request.args.get("minutes", type=int)))


# ----- Driver: send location (needs the bus's x-driver-key) -----

@app.post("/api/buses/<bus_ref>/location")
def location(bus_ref):
    return jsonify(svc.update_location(bus_ref, request.headers.get("x-driver-key"), body()))


# ----- Accounts: student, teacher, parent -----

@app.post("/api/auth/register")
def register():
    return jsonify(svc.register_user(body()))


@app.post("/api/auth/login")
def login():
    b = body()
    return jsonify(svc.login_user(b.get("email"), b.get("password")))


@app.get("/api/me")
@require_auth()
def me():
    """The logged-in person's trip(s): route, start point, pickup time, duration, live bus ETA.
    Parents get one trip per linked child."""
    return jsonify(svc.me_view(g.user))


# ----- Admin: add routes and buses -----

@app.post("/api/admin/routes")
@require_auth(["admin"])
def admin_route():
    return jsonify(svc.create_route(body()))


@app.post("/api/admin/buses")
@require_auth(["admin"])
def admin_bus():
    return jsonify(svc.create_bus(body()))


@app.get("/api/health")
def health():
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")

##### FILE: backend/__init__.py #####


##### FILE: backend/auth.py #####
"""Password hashing and signed login tokens using only the standard library."""
import base64
import hashlib
import hmac
import json
import os
import time
from functools import wraps

from flask import g, request

from .db import conn, one
from .errors import HttpError

SECRET = os.environ.get("TOKEN_SECRET", "dev-secret-change-me").encode()
TOKEN_DAYS = 7


def hash_password(password):
    salt = os.urandom(16)
    h = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=64)
    return salt.hex() + ":" + h.hex()


def verify_password(password, stored):
    try:
        salt_hex, hash_hex = stored.split(":")
        h = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2 ** 14, r=8, p=1, dklen=64)
        return hmac.compare_digest(h, bytes.fromhex(hash_hex))
    except ValueError:
        return False


def _b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _mac(body):
    return _b64(hmac.new(SECRET, body.encode(), hashlib.sha256).digest())


def sign(payload):
    payload = dict(payload, exp=time.time() + TOKEN_DAYS * 86400)
    body = _b64(json.dumps(payload).encode())
    return body + "." + _mac(body)


def verify(token):
    try:
        body, sig = (token or "").split(".")
        if not hmac.compare_digest(sig, _mac(body)):
            return None
        payload = json.loads(_unb64(body))
        return payload if payload["exp"] > time.time() else None
    except (ValueError, KeyError):
        return None


def require_auth(roles=None):
    """Decorator. @require_auth() = any logged-in user; @require_auth(["admin"]) = only those roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            payload = verify(request.headers.get("Authorization", "").replace("Bearer ", "", 1))
            if not payload:
                raise HttpError(401, "Please log in")
            with conn() as c:
                user = one(c, "SELECT id, name, email, role, route_id, stop_id, link_code FROM users WHERE id = ?", (payload["uid"],))
            if not user:
                raise HttpError(401, "Please log in")
            if roles and user["role"] not in roles:
                raise HttpError(403, "Not allowed for your account type")
            g.user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator

##### FILE: backend/db.py #####
"""SQLite database (Python standard library). Schema lives here."""
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.environ.get("DB_PATH") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "campusride.db")
_memory = None  # one shared connection when DB_PATH=":memory:" (used by tests)

SCHEMA = """
CREATE TABLE IF NOT EXISTS routes (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  name           TEXT NOT NULL,
  color          TEXT NOT NULL DEFAULT '#0f9d8a',
  departure_time TEXT NOT NULL DEFAULT '07:00',  -- morning: first stop to college
  return_time    TEXT NOT NULL DEFAULT '16:30'   -- evening: college back to first stop
);

-- The last stop of a route is the college. minutes_from_start is the planned
-- time after departure when the bus reaches that stop (first stop = 0).
CREATE TABLE IF NOT EXISTS stops (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  route_id           INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
  name               TEXT NOT NULL,
  lat                REAL NOT NULL,
  lng                REAL NOT NULL,
  seq                INTEGER NOT NULL,
  minutes_from_start INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS buses (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  label      TEXT NOT NULL UNIQUE,
  route_id   INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
  driver_key TEXT NOT NULL,
  lat        REAL,
  lng        REAL,
  speed      REAL,
  updated_at INTEGER
);

CREATE TABLE IF NOT EXISTS location_history (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  bus_id INTEGER NOT NULL REFERENCES buses(id) ON DELETE CASCADE,
  lat    REAL NOT NULL,
  lng    REAL NOT NULL,
  speed  REAL,
  ts     INTEGER NOT NULL
);

-- Students and teachers have a route and boarding stop. Parents link to students.
-- link_code lets a student share access with a parent (parent needs email + code).
CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL,
  email         TEXT NOT NULL UNIQUE,
  role          TEXT NOT NULL CHECK (role IN ('student','teacher','parent','admin')),
  password_hash TEXT NOT NULL,
  route_id      INTEGER REFERENCES routes(id) ON DELETE SET NULL,
  stop_id       INTEGER REFERENCES stops(id) ON DELETE SET NULL,
  link_code     TEXT
);

CREATE TABLE IF NOT EXISTS parent_children (
  parent_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY (parent_id, student_id)
);

CREATE INDEX IF NOT EXISTS idx_stops_route ON stops(route_id, seq);
CREATE INDEX IF NOT EXISTS idx_history_bus_ts ON location_history(bus_id, ts);
"""


def _open(path):
    c = sqlite3.connect(path, timeout=10, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def _connect():
    global _memory
    if DB_PATH == ":memory:":
        if _memory is None:
            _memory = _open(":memory:")
        return _memory
    return _open(DB_PATH)


@contextmanager
def conn():
    """Use as: with conn() as c: c.execute(...). Commits on success, rolls back on error."""
    c = _connect()
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        if c is not _memory:
            c.close()


def rows(c, sql, args=()):
    return [dict(r) for r in c.execute(sql, args).fetchall()]


def one(c, sql, args=()):
    r = c.execute(sql, args).fetchone()
    return dict(r) if r else None


def init_schema():
    with conn() as c:
        c.executescript(SCHEMA)


def reset_schema():
    with conn() as c:
        c.executescript("""DROP TABLE IF EXISTS parent_children; DROP TABLE IF EXISTS users;
            DROP TABLE IF EXISTS location_history; DROP TABLE IF EXISTS buses;
            DROP TABLE IF EXISTS stops; DROP TABLE IF EXISTS routes;""")
    init_schema()


init_schema()

##### FILE: backend/errors.py #####
class HttpError(Exception):
    """Raised anywhere in the backend; the Flask app turns it into a JSON error."""
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message

##### FILE: backend/seed.py #####
"""Loads a sample college in Pallavaram with two bus routes, demo buses and demo users.
Run: python -m backend.seed   (this wipes existing data)
Stop positions and timings are approximate samples. Replace them with your real bus plan."""
from .auth import hash_password
from .db import conn, one, reset_schema

# [name, lat, lng, minutes after departure]
ROUTES = [
    {"name": "Beach to Pallavaram (Local Line Route)", "color": "#0f9d8a", "departure_time": "06:30",
     "return_time": "16:30", "buses": ["A1", "A2"], "stops": [
        ("Chennai Beach", 13.0953, 80.2922, 0), ("Chennai Fort", 13.0866, 80.2859, 5),
        ("Chennai Park", 13.0766, 80.2745, 9), ("Chennai Egmore", 13.0780, 80.2610, 15),
        ("Chetpet", 13.0717, 80.2423, 21), ("Nungambakkam", 13.0599, 80.2425, 25),
        ("Kodambakkam", 13.0505, 80.2270, 30), ("Mambalam", 13.0394, 80.2212, 34),
        ("Saidapet", 13.0227, 80.2236, 39), ("Guindy", 13.0095, 80.2208, 44),
        ("St. Thomas Mount", 12.9955, 80.1985, 49), ("Pazhavanthangal", 12.9921, 80.1930, 52),
        ("Meenambakkam", 12.9866, 80.1745, 56), ("Trisulam", 12.9830, 80.1680, 60),
        ("Pallavaram", 12.9676, 80.1507, 66), ("College Campus, Pallavaram", 12.9655, 80.1500, 70)]},
    {"name": "Tambaram to Pallavaram", "color": "#c2307a", "departure_time": "07:30",
     "return_time": "16:30", "buses": ["B1"], "stops": [
        ("Tambaram", 12.9266, 80.1177, 0), ("Tambaram Sanatorium", 12.9364, 80.1213, 6),
        ("Chromepet", 12.9516, 80.1408, 12), ("Pallavaram", 12.9676, 80.1507, 20),
        ("College Campus, Pallavaram", 12.9655, 80.1500, 24)]},
]


def seed():
    reset_schema()
    with conn() as c:
        stop_id = {}
        for ri, r in enumerate(ROUTES):
            rid = c.execute("INSERT INTO routes (name, color, departure_time, return_time) VALUES (?, ?, ?, ?)",
                            (r["name"], r["color"], r["departure_time"], r["return_time"])).lastrowid
            r["id"] = rid
            for i, (name, lat, lng, mins) in enumerate(r["stops"]):
                stop_id[(ri, name)] = c.execute(
                    "INSERT INTO stops (route_id, name, lat, lng, seq, minutes_from_start) VALUES (?, ?, ?, ?, ?, ?)",
                    (rid, name, lat, lng, i, mins)).lastrowid
            for label in r["buses"]:
                c.execute("INSERT INTO buses (label, route_id, driver_key) VALUES (?, ?, ?)", (label, rid, f"demo-key-{label}"))

        def add_user(name, email, role, pw, route=None, stop=None, code=None):
            return c.execute("INSERT INTO users (name, email, role, password_hash, route_id, stop_id, link_code) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (name, email, role, hash_password(pw), route, stop, code)).lastrowid

        add_user("Admin", "admin@campus.test", "admin", "admin123")
        arun = add_user("Arun (student)", "arun@campus.test", "student", "demo123", ROUTES[0]["id"], stop_id[(0, "Guindy")], "123456")
        add_user("Priya (student)", "priya@campus.test", "student", "demo123", ROUTES[1]["id"], stop_id[(1, "Chromepet")], "654321")
        add_user("Mrs. Lakshmi (teacher)", "lakshmi@campus.test", "teacher", "demo123", ROUTES[0]["id"], stop_id[(0, "Saidapet")])
        parent = add_user("Arun's parent", "parent@campus.test", "parent", "demo123")
        c.execute("INSERT INTO parent_children (parent_id, student_id) VALUES (?, ?)", (parent, arun))

        # ---- More demo people (all use password demo123) ----
        a, b = ROUTES[0]["id"], ROUTES[1]["id"]
        sid = lambda ri, name: stop_id[(ri, name)]

        # 3 more students (route, boarding stop, family code)
        karthik = add_user("Karthik (student)", "karthik@campus.test", "student", "demo123", a, sid(0, "Meenambakkam"), "111111")
        divya = add_user("Divya (student)", "divya@campus.test", "student", "demo123", a, sid(0, "Chetpet"), "222222")
        rahul = add_user("Rahul (student)", "rahul@campus.test", "student", "demo123", b, sid(1, "Tambaram"), "333333")
        priya = one(c, "SELECT id FROM users WHERE email = 'priya@campus.test'")["id"]

        # 3 more teachers
        add_user("Mr. Venkatesh (teacher)", "venkatesh@campus.test", "teacher", "demo123", a, sid(0, "Kodambakkam"))
        add_user("Ms. Fathima (teacher)", "fathima@campus.test", "teacher", "demo123", b, sid(1, "Tambaram Sanatorium"))
        add_user("Dr. Rajan (teacher)", "rajan@campus.test", "teacher", "demo123", a, sid(0, "Chennai Park"))

        # 5 more parents. Some children have two parents, and one parent follows two children.
        ramesh = add_user("Ramesh (Karthik's father)", "ramesh@campus.test", "parent", "demo123")
        meena = add_user("Meena (Karthik's mother)", "meena@campus.test", "parent", "demo123")
        suresh = add_user("Suresh (Divya's father)", "suresh@campus.test", "parent", "demo123")
        kavitha = add_user("Kavitha (mother of Priya and Rahul)", "kavitha@campus.test", "parent", "demo123")
        anitha = add_user("Anitha (Priya's mother)", "anitha@campus.test", "parent", "demo123")
        for parent_id, student_id in [(ramesh, karthik), (meena, karthik), (suresh, divya),
                                      (kavitha, priya), (kavitha, rahul), (anitha, priya)]:
            c.execute("INSERT INTO parent_children (parent_id, student_id) VALUES (?, ?)", (parent_id, student_id))


if __name__ == "__main__":
    seed()
    print("Seeded 5 students, 4 teachers, 6 parents and 1 admin. All demo passwords are demo123 (admin: admin123).")
    print("Students: arun, priya, karthik, divya, rahul  (@campus.test)")
    print("Teachers: lakshmi, venkatesh, fathima, rajan  (@campus.test)")
    print("Parents:  parent, ramesh, meena, suresh, kavitha, anitha  (@campus.test)")
    print("Driver keys: demo-key-A1, demo-key-A2, demo-key-B1")

##### FILE: backend/service.py #####
"""Business logic: schedules, durations, live ETA, sign up and login."""
import math
import os
import random
import re
import time

from .auth import hash_password, sign, verify_password
from .db import conn, one, rows
from .errors import HttpError

STALE_SECONDS = int(os.environ.get("STALE_SECONDS", 60))
AVG_SPEED_KMH = float(os.environ.get("AVG_SPEED_KMH", 20))


def now():
    return int(time.time())


def haversine_km(lat1, lng1, lat2, lng2):
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat, dlng = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def add_minutes(hhmm, minutes):
    h, m = (int(x) for x in hhmm.split(":"))
    t = (h * 60 + m + minutes) % 1440
    return f"{t // 60:02d}:{t % 60:02d}"


# ---------- Routes and schedules ----------

def route_detail(route_id, direction="morning"):
    """direction 'morning' = first stop to college; 'evening' = college back to first stop."""
    with conn() as c:
        r = one(c, "SELECT * FROM routes WHERE id = ?", (route_id,))
        if not r:
            return None
        stops = rows(c, "SELECT id, name, lat, lng, minutes_from_start FROM stops WHERE route_id = ? ORDER BY seq", (route_id,))
    total = stops[-1]["minutes_from_start"] if stops else 0
    evening = direction == "evening"
    if evening:
        stops = [dict(s, minutes_from_start=total - s["minutes_from_start"]) for s in reversed(stops)]
    departure = r["return_time"] if evening else r["departure_time"]
    for i, s in enumerate(stops):
        s["seq"] = i
        s["scheduled_time"] = add_minutes(departure, s["minutes_from_start"])
    return {
        "id": r["id"], "name": r["name"], "color": r["color"],
        "direction": "evening" if evening else "morning",
        "start_point": stops[0]["name"] if stops else None,
        "end_point": stops[-1]["name"] if stops else None,
        "departure_time": departure,
        "arrival_time": stops[-1]["scheduled_time"] if stops else None,
        "total_minutes": total, "stop_count": len(stops), "stops": stops,
    }


def list_routes(direction="morning"):
    with conn() as c:
        ids = [r["id"] for r in rows(c, "SELECT id FROM routes ORDER BY id")]
    return [route_detail(i, direction) for i in ids]


def create_route(data):
    hhmm = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
    name = str(data.get("name") or "").strip()
    dep, ret, stops = data.get("departure_time"), data.get("return_time"), data.get("stops")
    if not name:
        raise HttpError(400, "Route name is required")
    if not (isinstance(dep, str) and hhmm.match(dep) and isinstance(ret, str) and hhmm.match(ret)):
        raise HttpError(400, "Times must look like 07:15")
    if not isinstance(stops, list) or len(stops) < 2:
        raise HttpError(400, "A route needs at least 2 stops")
    prev = 0
    for i, s in enumerate(stops, 1):
        ok = (isinstance(s, dict) and str(s.get("name") or "").strip()
              and all(isinstance(s.get(k), (int, float)) and not isinstance(s.get(k), bool) for k in ("lat", "lng", "minutes_from_start")))
        if not ok:
            raise HttpError(400, f"Stop {i} needs name, lat, lng and minutes_from_start")
        if s["minutes_from_start"] < prev:
            raise HttpError(400, "minutes_from_start must not decrease")
        prev = s["minutes_from_start"]
    with conn() as c:
        rid = c.execute("INSERT INTO routes (name, color, departure_time, return_time) VALUES (?, ?, ?, ?)",
                        (name, data.get("color") or "#0f9d8a", dep, ret)).lastrowid
        for i, s in enumerate(stops):
            c.execute("INSERT INTO stops (route_id, name, lat, lng, seq, minutes_from_start) VALUES (?, ?, ?, ?, ?, ?)",
                      (rid, s["name"].strip(), s["lat"], s["lng"], i, s["minutes_from_start"]))
    return route_detail(rid)


def create_bus(data):
    label, key = str(data.get("label") or "").strip(), str(data.get("driver_key") or "").strip()
    if not label or not key:
        raise HttpError(400, "label and driver_key are required")
    with conn() as c:
        if not one(c, "SELECT 1 AS x FROM routes WHERE id = ?", (data.get("route_id"),)):
            raise HttpError(400, "Unknown route")
        if one(c, "SELECT 1 AS x FROM buses WHERE label = ?", (label,)):
            raise HttpError(409, "A bus with that label already exists")
        bid = c.execute("INSERT INTO buses (label, route_id, driver_key) VALUES (?, ?, ?)", (label, data["route_id"], key)).lastrowid
    return {"id": bid, "label": label, "route_id": data["route_id"]}


# ---------- Live buses ----------

def list_buses(route_id=None):
    sql = """SELECT b.id, b.label, b.route_id, r.name AS route_name, r.color, b.lat, b.lng, b.speed, b.updated_at
             FROM buses b JOIN routes r ON r.id = b.route_id"""
    args = ()
    if route_id:
        sql += " WHERE b.route_id = ?"
        args = (route_id,)
    with conn() as c:
        buses = rows(c, sql + " ORDER BY b.label", args)
    t = now()
    for b in buses:
        u = b["updated_at"]
        b["online"] = u is not None and t - u <= STALE_SECONDS
        b["seconds_ago"] = None if u is None else t - u
    return buses


def update_location(bus_ref, driver_key, body):
    with conn() as c:
        bus = one(c, "SELECT id, driver_key FROM buses WHERE id = ? OR label = ?", (int(bus_ref) if str(bus_ref).isdigit() else -1, bus_ref))
        if not bus:
            raise HttpError(404, "Bus not found")
        if driver_key != bus["driver_key"]:
            raise HttpError(401, "Invalid driver key")
        lat, lng, speed = body.get("lat"), body.get("lng"), body.get("speed")
        num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
        if not (num(lat) and num(lng) and -90 <= lat <= 90 and -180 <= lng <= 180):
            raise HttpError(400, "lat and lng must be valid numbers")
        speed = float(speed) if num(speed) else None
        ts = now()
        c.execute("UPDATE buses SET lat = ?, lng = ?, speed = ?, updated_at = ? WHERE id = ?", (lat, lng, speed, ts, bus["id"]))
        c.execute("INSERT INTO location_history (bus_id, lat, lng, speed, ts) VALUES (?, ?, ?, ?, ?)", (bus["id"], lat, lng, speed, ts))
    return {"ok": True, "ts": ts}


def bus_history(bus_ref, minutes):
    minutes = min(minutes or 30, 240)
    with conn() as c:
        return rows(c, """SELECT h.lat, h.lng, h.speed, h.ts FROM location_history h JOIN buses b ON b.id = h.bus_id
            WHERE (b.id = ? OR b.label = ?) AND h.ts >= ? ORDER BY h.ts""",
                    (int(bus_ref) if str(bus_ref).isdigit() else -1, bus_ref, now() - minutes * 60))


def buses_eta(route_id, lat, lng):
    """Straight-line distance / average speed for each online bus on the route."""
    t = now()
    with conn() as c:
        buses = rows(c, "SELECT label, lat, lng, updated_at FROM buses WHERE route_id = ? AND lat IS NOT NULL", (route_id,))
    out = []
    for b in buses:
        if t - b["updated_at"] > STALE_SECONDS:
            continue
        km = haversine_km(b["lat"], b["lng"], lat, lng)
        out.append({"bus": b["label"], "distance_km": round(km, 2), "eta_minutes": max(0, round(km / AVG_SPEED_KMH * 60))})
    return sorted(out, key=lambda x: x["eta_minutes"])


def stop_eta(stop_id):
    with conn() as c:
        stop = one(c, "SELECT * FROM stops WHERE id = ?", (stop_id,))
    if not stop:
        raise HttpError(404, "Stop not found")
    return {"stop": {"id": stop["id"], "name": stop["name"]}, "buses": buses_eta(stop["route_id"], stop["lat"], stop["lng"])}


# ---------- Users ----------

def register_user(data):
    name = str(data.get("name") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    password, role = str(data.get("password") or ""), data.get("role")
    if not name:
        raise HttpError(400, "Name is required")
    if not re.match(r"^\S+@\S+\.\S+$", email):
        raise HttpError(400, "Enter a valid email")
    if len(password) < 6:
        raise HttpError(400, "Password must be at least 6 characters")
    if role not in ("student", "teacher", "parent"):
        raise HttpError(400, "Role must be student, teacher or parent")
    route_id = stop_id = child = link_code = None
    with conn() as c:
        if one(c, "SELECT 1 AS x FROM users WHERE email = ?", (email,)):
            raise HttpError(409, "That email is already registered")
        if role == "parent":
            child = one(c, "SELECT id FROM users WHERE email = ? AND role = 'student' AND link_code = ?",
                        (str(data.get("child_email") or "").strip().lower(), str(data.get("link_code") or "").strip()))
            if not child:
                raise HttpError(400, "Child's email or family code is wrong. Ask your child for the code shown on their dashboard.")
        else:
            try:
                route_id, stop_id = int(data.get("route_id")), int(data.get("stop_id"))
            except (TypeError, ValueError):
                raise HttpError(400, "Choose a valid route and boarding stop")
            if not one(c, "SELECT 1 AS x FROM stops WHERE id = ? AND route_id = ?", (stop_id, route_id)):
                raise HttpError(400, "Choose a valid route and boarding stop")
            if role == "student":
                link_code = str(random.SystemRandom().randint(100000, 999999))
        uid = c.execute("INSERT INTO users (name, email, role, password_hash, route_id, stop_id, link_code) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (name, email, role, hash_password(password), route_id, stop_id, link_code)).lastrowid
        if child:
            c.execute("INSERT INTO parent_children (parent_id, student_id) VALUES (?, ?)", (uid, child["id"]))
    return {"token": sign({"uid": uid}), "user": {"id": uid, "name": name, "email": email, "role": role}}


def login_user(email, password):
    with conn() as c:
        u = one(c, "SELECT * FROM users WHERE email = ?", (str(email or "").strip().lower(),))
    if not u or not verify_password(str(password or ""), u["password_hash"]):
        raise HttpError(401, "Wrong email or password")
    return {"token": sign({"uid": u["id"]}), "user": {"id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"]}}


def trip_for(u):
    """Everything a student, teacher or child needs to see about their bus trip."""
    if not u.get("route_id"):
        return None
    morning, evening = route_detail(u["route_id"], "morning"), route_detail(u["route_id"], "evening")
    stop = next((s for s in morning["stops"] if s["id"] == u["stop_id"]), None) if morning else None
    if not stop:
        return None
    back = next(s for s in evening["stops"] if s["id"] == u["stop_id"])
    return {
        "person": u["name"], "route": morning, "evening_route": evening,
        "boarding_stop": {"id": stop["id"], "name": stop["name"]},
        "morning_pickup_time": stop["scheduled_time"],
        "minutes_to_college": morning["total_minutes"] - stop["minutes_from_start"],
        "evening_drop_time": back["scheduled_time"],
        "buses": buses_eta(u["route_id"], stop["lat"], stop["lng"]),
    }


def me_view(user):
    base = {k: v for k, v in user.items() if k != "link_code"}
    if user["role"] == "student":
        return {"user": dict(base, link_code=user["link_code"]), "trips": [t for t in [trip_for(user)] if t]}
    if user["role"] == "teacher":
        return {"user": base, "trips": [t for t in [trip_for(user)] if t]}
    if user["role"] == "parent":
        with conn() as c:
            kids = rows(c, """SELECT u.id, u.name, u.route_id, u.stop_id FROM parent_children pc
                JOIN users u ON u.id = pc.student_id WHERE pc.parent_id = ?""", (user["id"],))
        return {"user": base, "trips": [t for t in map(trip_for, kids) if t]}
    return {"user": base, "trips": []}

##### FILE: backend/simulate.py #####
"""Fakes GPS from every bus so you can demo without a real driver phone.
Start the server first (python app.py), then run: python -m backend.simulate"""
import json
import os
import time
import urllib.request

BASE = os.environ.get("API_URL", "http://localhost:5000")


def call(path, body=None, headers=None):
    req = urllib.request.Request(BASE + path, headers={"Content-Type": "application/json", **(headers or {})},
                                 data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.load(r)


def main():
    routes = {r["id"]: r for r in call("/api/routes")}
    sims = []
    for i, b in enumerate(call("/api/buses")):
        stops = routes[b["route_id"]]["stops"]
        sims.append({"label": b["label"], "stops": stops, "pos": (i * 2.5) % len(stops)})
    print(f"Simulating {len(sims)} buses. Press Ctrl+C to stop.")
    while True:
        for s in sims:
            n = len(s["stops"])
            s["pos"] = (s["pos"] + 0.04) % n
            i, t = int(s["pos"]), s["pos"] - int(s["pos"])
            a, b = s["stops"][i], s["stops"][(i + 1) % n]
            try:
                call(f"/api/buses/{s['label']}/location",
                     {"lat": a["lat"] + (b["lat"] - a["lat"]) * t, "lng": a["lng"] + (b["lng"] - a["lng"]) * t, "speed": 20},
                     {"x-driver-key": f"demo-key-{s['label']}"})
            except Exception as e:
                print("error:", e)
        time.sleep(2)


if __name__ == "__main__":
    main()

##### FILE: public/app.js #####
const map = L.map('map').setView([13.012, 80.238], 15);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19, attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let routes = [], filter = null;
const busMarkers = {};
const lines = {}, stopMarkers = [];

const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const getJSON = async url => { const r = await fetch(url); if (!r.ok) throw new Error(r.status); return r.json(); };

async function loadRoutes() {
  routes = await getJSON('/api/routes');
  const bounds = [];
  routes.forEach(r => {
    const pts = r.stops.map(s => [s.lat, s.lng]);
    lines[r.id] = L.polygon(pts, { color: r.color, weight: 5, fill: false }).addTo(map);
    r.stops.forEach(s => {
      bounds.push([s.lat, s.lng]);
      const m = L.circleMarker([s.lat, s.lng], { radius: 7, color: '#14213d', weight: 2, fillColor: '#fff', fillOpacity: 1 }).addTo(map);
      m.routeId = r.id;
      m.bindPopup(`<b>${esc(s.name)}</b><br>${esc(r.name)}<br><span>Loading…</span>`);
      m.on('popupopen', async () => {
        try {
          const d = await getJSON(`/api/stops/${s.id}/eta`);
          const body = d.buses.length
            ? d.buses.map(b => `Bus ${esc(b.bus)}: ${b.eta_minutes < 1 ? 'arriving' : b.eta_minutes + ' min'}`).join('<br>')
            : 'No buses online on this route';
          m.setPopupContent(`<b>${esc(s.name)}</b><br>${esc(r.name)}<br>${body}`);
        } catch { m.setPopupContent('Could not load arrival times'); }
      });
      stopMarkers.push(m);
    });
  });
  if (bounds.length) map.fitBounds(bounds, { padding: [30, 30] });
  drawChips();
}

function drawChips() {
  const el = document.getElementById('chips');
  el.innerHTML = '';
  const make = (label, color, id) => {
    const b = document.createElement('button');
    b.className = 'chip';
    b.setAttribute('aria-pressed', filter === id);
    b.innerHTML = (color ? `<i style="background:${color}"></i>` : '') + esc(label);
    b.onclick = () => { filter = id; drawChips(); refreshBuses(); applyFilter(); showSummary(); };
    el.appendChild(b);
  };
  make('All routes', null, null);
  routes.forEach(r => make(r.name, r.color, r.id));
}

function showSummary() {
  const r = routes.find(x => x.id === filter);
  document.getElementById('summary').textContent = r
    ? `${r.start_point} to ${r.end_point}, departs ${r.departure_time}, ${r.total_minutes} min, ${r.stop_count} stops`
    : '';
}

function applyFilter() {
  routes.forEach(r => lines[r.id].setStyle({ opacity: filter === null || filter === r.id ? 1 : 0.2 }));
}

async function refreshBuses() {
  let buses;
  try { buses = await getJSON('/api/buses'); } catch { return; }
  const list = document.getElementById('buses');
  const shown = buses.filter(b => filter === null || b.route_id === filter);
  list.innerHTML = shown.map(b => `<div class="bus ${b.online ? '' : 'off'}">
      <span><b>${esc(b.label)}</b> · ${esc(b.route_name)}</span>
      <span class="mute">${b.online ? b.seconds_ago + 's ago' : 'offline'}</span></div>`).join('') || '<span class="mute">No buses</span>';

  const seen = new Set();
  shown.forEach(b => {
    if (!b.online || b.lat == null) return;
    seen.add(b.id);
    const icon = L.divIcon({
      className: '', iconSize: [26, 26],
      html: `<div class="busicon" style="background:${b.color}">${esc(b.label)}</div>`
    });
    if (busMarkers[b.id]) busMarkers[b.id].setLatLng([b.lat, b.lng]).setIcon(icon);
    else busMarkers[b.id] = L.marker([b.lat, b.lng], { icon }).addTo(map);
  });
  Object.keys(busMarkers).forEach(id => {
    if (!seen.has(Number(id))) { map.removeLayer(busMarkers[id]); delete busMarkers[id]; }
  });
}

loadRoutes().then(() => { refreshBuses(); setInterval(refreshBuses, 3000); });

##### FILE: public/dashboard.html #####
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CampusRide: my bus</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header><h1>My bus</h1><span><a href="index.html">Live map</a> · <button class="link" id="logout">Log out</button></span></header>
<div class="page">
  <p id="hello" class="mute"></p>
  <div class="tabs" role="group" aria-label="Trip direction">
    <button class="chip" id="dMorning" aria-pressed="true">To college</button>
    <button class="chip" id="dEvening" aria-pressed="false">Back home</button>
  </div>
  <div id="trips"><p class="mute">Loading…</p></div>
</div>
<script src="dashboard.js"></script>
</body>
</html>

##### FILE: public/dashboard.js #####
let token = null;
try { token = localStorage.getItem('token'); } catch {}
if (!token) location.href = 'login.html';

let dir = 'morning', data = null;
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const dur = m => (m >= 60 ? `${Math.floor(m / 60)} h ${m % 60} min` : `${m} min`);

async function load() {
  const r = await fetch('/api/me', { headers: { Authorization: 'Bearer ' + token } });
  if (r.status === 401) { try { localStorage.removeItem('token'); } catch {} location.href = 'login.html'; return; }
  data = await r.json();
  render();
}

function tripCard(t) {
  const route = dir === 'morning' ? t.route : t.evening_route;
  const mine = t.boarding_stop.id;
  const live = t.buses.length
    ? t.buses.map(b => `Bus ${esc(b.bus)}: ${b.eta_minutes < 1 ? 'arriving now' : b.eta_minutes + ' min away'} (${b.distance_km} km)`).join('<br>')
    : 'No bus is sharing its location right now';
  const mineTime = route.stops.find(s => s.id === mine).scheduled_time;
  return `<section class="card">
    <h2>${esc(t.person)}: ${esc(route.name)}</h2>
    <div class="facts">
      <div class="fact"><small>Starts at</small><b>${esc(route.start_point)}</b></div>
      <div class="fact"><small>Departs</small><b>${route.departure_time}</b></div>
      <div class="fact"><small>Ends at</small><b>${esc(route.end_point)}</b></div>
      <div class="fact"><small>Arrives</small><b>${route.arrival_time}</b></div>
      <div class="fact"><small>Total journey</small><b>${dur(route.total_minutes)}</b></div>
      <div class="fact"><small>Stops</small><b>${route.stop_count}</b></div>
      <div class="fact"><small>${dir === 'morning' ? 'Pickup at' : 'Drop at'} ${esc(t.boarding_stop.name)}</small><b>${mineTime}</b></div>
      ${dir === 'morning' ? `<div class="fact"><small>From pickup to college</small><b>${dur(t.minutes_to_college)}</b></div>` : ''}
    </div>
    <h2>Live bus</h2>
    <p>${live}</p>
    <h2>Stops and planned times</h2>
    <ol class="timeline">${route.stops.map(s =>
      `<li class="${s.id === mine ? 'mine' : ''}"${s.id === mine ? ' aria-current="true"' : ''}><time>${s.scheduled_time}</time><span>${esc(s.name)}${s.id === mine ? ' (your stop)' : ''}</span></li>`).join('')}</ol>
  </section>`;
}

function render() {
  const u = data.user;
  $('hello').textContent = `Signed in as ${u.name} (${u.role})`;
  let html = '';
  if (u.role === 'student' && u.link_code) {
    html += `<div class="card"><b>Family code: ${esc(u.link_code)}</b><p class="mute">Give this code and your email to your parent so they can sign up and follow your bus.</p></div>`;
  }
  if (u.role === 'admin') html += '<div class="card">Admins add routes and buses through the API. See the README.</div>';
  html += data.trips.length ? data.trips.map(tripCard).join('') : (u.role === 'admin' ? '' : '<p class="mute">No bus trip linked to this account yet.</p>');
  $('trips').innerHTML = html;
}

function setDir(d) {
  dir = d;
  $('dMorning').setAttribute('aria-pressed', d === 'morning'); $('dEvening').setAttribute('aria-pressed', d === 'evening');
  if (data) render();
}
$('dMorning').onclick = () => setDir('morning'); $('dEvening').onclick = () => setDir('evening');
$('logout').onclick = () => { try { localStorage.removeItem('token'); } catch {} location.href = 'login.html'; };

load();
setInterval(load, 10000);

##### FILE: public/driver.html #####
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CampusRide: driver</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header><h1>Driver page</h1><a href="index.html">Student view</a></header>
<form class="driver" id="f" style="padding:0 20px">
  <label>Bus number<input id="bus" placeholder="A1" required autocomplete="off"></label>
  <label>Driver key<input id="key" type="password" required autocomplete="off"></label>
  <button class="btn" id="go" type="submit">Start sharing location</button>
  <p id="status" class="mute" role="status">Keep this page open while driving. Location sharing needs HTTPS (or localhost).</p>
</form>
<script>
let watchId = null, lastSent = 0;
const $ = id => document.getElementById(id);
const status = t => $('status').textContent = t;

$('f').addEventListener('submit', e => {
  e.preventDefault();
  if (watchId !== null) { navigator.geolocation.clearWatch(watchId); watchId = null; $('go').textContent = 'Start sharing location'; $('go').classList.remove('stop'); return status('Stopped sharing.'); }
  if (!navigator.geolocation) return status('This browser does not support location.');
  $('go').textContent = 'Stop sharing'; $('go').classList.add('stop');
  watchId = navigator.geolocation.watchPosition(async pos => {
    if (Date.now() - lastSent < 3000) return;
    lastSent = Date.now();
    try {
      const r = await fetch(`/api/buses/${encodeURIComponent($('bus').value.trim())}/location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-driver-key': $('key').value },
        body: JSON.stringify({ lat: pos.coords.latitude, lng: pos.coords.longitude,
          speed: pos.coords.speed == null ? null : pos.coords.speed * 3.6 })
      });
      const d = await r.json();
      status(r.ok ? 'Sharing. Last update ' + new Date().toLocaleTimeString() : 'Error: ' + d.error);
    } catch { status('Network problem. Will retry on the next update.'); }
  }, err => status('Location error: ' + err.message), { enableHighAccuracy: true, maximumAge: 2000 });
});
</script>
</body>
</html>

##### FILE: public/index.html #####
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CampusRide: live bus tracker</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header><h1>CampusRide</h1><span><a href="login.html">Log in</a> · <a href="driver.html">Driver page</a></span></header>
<div class="layout">
  <aside class="panel">
    <div class="chips" id="chips" role="group" aria-label="Filter by route"></div>
    <div id="summary" class="mute" aria-live="polite"></div>
    <h2>Buses</h2>
    <div id="buses"><span class="mute">Loading…</span></div>
    <p class="mute">Tap a stop on the map to see arrival times.</p>
  </aside>
  <div id="map"></div>
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="app.js"></script>
</body>
</html>

##### FILE: public/login.html #####
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CampusRide: log in</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header><h1>CampusRide</h1><a href="index.html">Live map</a></header>
<div class="page">
  <div class="tabs" role="group" aria-label="Log in or sign up">
    <button class="chip" id="tabLogin" aria-pressed="true">Log in</button>
    <button class="chip" id="tabReg" aria-pressed="false">Sign up</button>
  </div>

  <form class="auth" id="loginForm">
    <label>Email<input type="email" id="lEmail" required autocomplete="username"></label>
    <label>Password<input type="password" id="lPass" required autocomplete="current-password"></label>
    <button class="btn" type="submit">Log in</button>
    <p class="mute">Demo: arun@campus.test, lakshmi@campus.test or parent@campus.test (password demo123)</p>
    <p class="msg" id="lMsg" role="alert"></p>
  </form>

  <form class="auth" id="regForm" hidden>
    <label>Full name<input id="rName" required></label>
    <label>Email<input type="email" id="rEmail" required autocomplete="username"></label>
    <label>Password (6+ characters)<input type="password" id="rPass" minlength="6" required autocomplete="new-password"></label>
    <label>I am a
      <select id="rRole"><option value="student">Student</option><option value="teacher">Teacher</option><option value="parent">Parent</option></select>
    </label>
    <div id="busFields" style="display:grid;gap:12px">
      <label>Bus route<select id="rRoute"></select></label>
      <label>My boarding stop<select id="rStop"></select></label>
    </div>
    <div id="parentFields" style="display:none;gap:12px">
      <label>Child's email<input type="email" id="rChild"></label>
      <label>Family code (shown on your child's dashboard)<input id="rCode" inputmode="numeric"></label>
    </div>
    <button class="btn" type="submit">Create account</button>
    <p class="msg" id="rMsg" role="alert"></p>
  </form>
</div>
<script>
const $ = id => document.getElementById(id);
let routes = [];

function show(tab) {
  $('loginForm').hidden = tab !== 'login'; $('regForm').hidden = tab !== 'reg';
  $('tabLogin').setAttribute('aria-pressed', tab === 'login'); $('tabReg').setAttribute('aria-pressed', tab === 'reg');
}
$('tabLogin').onclick = () => show('login'); $('tabReg').onclick = () => show('reg');

function fillStops() {
  const r = routes.find(x => x.id === Number($('rRoute').value));
  $('rStop').innerHTML = '';
  (r ? r.stops : []).forEach(s => $('rStop').add(new Option(`${s.name} (${s.scheduled_time})`, s.id)));
}
fetch('/api/routes').then(r => r.json()).then(d => {
  routes = d;
  d.forEach(r => $('rRoute').add(new Option(`${r.name}, starts ${r.departure_time}`, r.id)));
  fillStops();
});
$('rRoute').onchange = fillStops;
$('rRole').onchange = () => {
  const parent = $('rRole').value === 'parent';
  $('busFields').style.display = parent ? 'none' : 'grid';
  $('parentFields').style.display = parent ? 'grid' : 'none';
};

async function post(url, body, msgEl) {
  msgEl.textContent = '';
  try {
    const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const d = await r.json();
    if (!r.ok) { msgEl.textContent = d.error || 'Something went wrong'; return; }
    try { localStorage.setItem('token', d.token); } catch {}
    location.href = 'dashboard.html';
  } catch { msgEl.textContent = 'Network problem. Try again.'; }
}
$('loginForm').onsubmit = e => { e.preventDefault(); post('/api/auth/login', { email: $('lEmail').value, password: $('lPass').value }, $('lMsg')); };
$('regForm').onsubmit = e => {
  e.preventDefault();
  post('/api/auth/register', {
    name: $('rName').value, email: $('rEmail').value, password: $('rPass').value, role: $('rRole').value,
    route_id: Number($('rRoute').value), stop_id: Number($('rStop').value),
    child_email: $('rChild').value, link_code: $('rCode').value
  }, $('rMsg'));
};
</script>
</body>
</html>

##### FILE: public/style.css #####
:root{--bg:#eef2f5;--panel:#fff;--ink:#14213d;--mute:#5b6b80;--line:#d5dde5;--sel:#e8f1f8}
@media (prefers-color-scheme:dark){:root{--bg:#0f1722;--panel:#18222f;--ink:#e8eef5;--mute:#9aabbd;--line:#2a3747;--sel:#223044}}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg);color:var(--ink)}
header{display:flex;justify-content:space-between;align-items:baseline;padding:14px 20px}
h1{margin:0;font-size:1.4rem}
header a,.mute{color:var(--mute);font-size:.9rem}
.layout{display:grid;grid-template-columns:320px 1fr;gap:16px;padding:0 20px 20px;height:calc(100vh - 64px)}
@media(max-width:800px){.layout{grid-template-columns:1fr;height:auto}#map{height:60vh}}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px;overflow:auto}
#map{border-radius:12px;border:1px solid var(--line);min-height:320px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}
button,input{font:inherit;color:var(--ink)}
.chip{display:flex;align-items:center;gap:6px;background:none;border:1.5px solid var(--line);border-radius:999px;padding:6px 12px;cursor:pointer}
.chip i{width:11px;height:11px;border-radius:50%;display:block}
.chip[aria-pressed=true]{border-color:var(--ink);background:var(--sel);font-weight:600}
button:focus-visible,input:focus-visible{outline:3px solid #3b82f6;outline-offset:2px}
h2{font-size:1rem;margin:14px 0 6px}
.bus{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--line)}
.bus:last-child{border-bottom:0}
.off{opacity:.5}
.busicon{color:#fff;font-weight:700;font-size:11px;text-align:center;line-height:26px;width:26px;height:26px;border-radius:50%;border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4)}
form.driver{max-width:420px;margin:0 auto;display:grid;gap:12px}
form.driver label{display:grid;gap:4px}
form.driver input{padding:10px;border:1.5px solid var(--line);border-radius:8px;background:var(--panel)}
.btn{padding:12px;border:0;border-radius:8px;background:#0f9d8a;color:#fff;font-weight:700;cursor:pointer}
.btn.stop{background:#c2307a}
#status{min-height:3em}

/* accounts and dashboard */
.page{max-width:900px;margin:0 auto;padding:0 20px 30px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:16px}
.card h2{margin:0 0 4px;font-size:1.1rem}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:12px 0}
.fact{background:var(--sel);border-radius:10px;padding:10px}
.fact small{display:block;color:var(--mute)}
.fact b{font-size:1.05rem}
.timeline{list-style:none;margin:12px 0 0;padding:0 0 0 14px;border-left:3px solid var(--line)}
.timeline li{display:flex;gap:12px;padding:6px 0 6px 10px;position:relative}
.timeline li::before{content:"";position:absolute;left:-19px;top:13px;width:11px;height:11px;border-radius:50%;background:var(--panel);border:2.5px solid var(--mute)}
.timeline li.mine{font-weight:700}
.timeline li.mine::before{background:#0f9d8a;border-color:#0f9d8a}
.timeline time{min-width:48px;font-variant-numeric:tabular-nums;color:var(--mute)}
.tabs{display:flex;gap:8px;margin:0 0 14px}
.link{background:none;border:0;color:var(--mute);text-decoration:underline;cursor:pointer;font-size:.9rem}
.msg{color:#c2307a;min-height:1.4em}
form.auth{display:grid;gap:12px;max-width:440px;margin:0 auto}
form.auth label{display:grid;gap:4px}
form.auth input,form.auth select{padding:10px;border:1.5px solid var(--line);border-radius:8px;background:var(--panel);font:inherit;color:var(--ink)}

##### FILE: requirements.txt #####
Flask>=3.0

##### FILE: tests/test_app.py #####
"""Run with: python -m unittest discover -s tests   (uses an in-memory database)"""
import os
import sys
import unittest

os.environ["DB_PATH"] = ":memory:"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402
from backend import service as svc  # noqa: E402
from backend.db import conn  # noqa: E402
from backend.seed import seed  # noqa: E402


class CampusRideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed()
        cls.client = app.test_client()

    def login(self, email, password="demo123"):
        r = self.client.post("/api/auth/login", json={"email": email, "password": password})
        self.assertEqual(r.status_code, 200, r.get_json())
        return {"Authorization": "Bearer " + r.get_json()["token"]}

    def test_route_summary(self):
        r = self.client.get("/api/routes").get_json()[0]
        self.assertEqual(r["start_point"], "Chennai Beach")
        self.assertEqual(r["end_point"], "College Campus, Pallavaram")
        self.assertEqual((r["total_minutes"], r["stop_count"]), (70, 16))
        self.assertEqual((r["departure_time"], r["arrival_time"]), ("06:30", "07:40"))

    def test_evening_route_is_reversed(self):
        r = self.client.get("/api/routes/1?direction=evening").get_json()
        self.assertEqual(r["start_point"], "College Campus, Pallavaram")
        self.assertEqual(r["end_point"], "Chennai Beach")
        self.assertEqual((r["departure_time"], r["arrival_time"]), ("16:30", "17:40"))

    def test_student_dashboard(self):
        me = self.client.get("/api/me", headers=self.login("arun@campus.test")).get_json()
        t = me["trips"][0]
        self.assertEqual(t["boarding_stop"]["name"], "Guindy")
        self.assertEqual(t["morning_pickup_time"], "07:14")
        self.assertEqual(t["minutes_to_college"], 26)
        self.assertEqual(me["user"]["link_code"], "123456")

    def test_parent_sees_child_trip(self):
        me = self.client.get("/api/me", headers=self.login("parent@campus.test")).get_json()
        self.assertEqual(len(me["trips"]), 1)
        self.assertEqual(me["trips"][0]["person"], "Arun (student)")
        self.assertNotIn("link_code", me["user"])

    def test_auth_required_and_wrong_password(self):
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        r = self.client.post("/api/auth/login", json={"email": "arun@campus.test", "password": "nope"})
        self.assertEqual(r.status_code, 401)

    def test_parent_signup_needs_family_code(self):
        bad = {"name": "P", "email": "p2@x.com", "password": "secret1", "role": "parent", "child_email": "arun@campus.test", "link_code": "000000"}
        self.assertEqual(self.client.post("/api/auth/register", json=bad).status_code, 400)
        good = dict(bad, link_code="123456")
        self.assertEqual(self.client.post("/api/auth/register", json=good).status_code, 200)

    def test_student_stop_must_match_route(self):
        r = self.client.post("/api/auth/register", json={"name": "S", "email": "s@x.com", "password": "secret1", "role": "student", "route_id": 2, "stop_id": 1})
        self.assertEqual(r.status_code, 400)

    def test_driver_location_and_live_eta(self):
        url = "/api/buses/A1/location"
        pos = {"lat": 13.0227, "lng": 80.2236, "speed": 20}
        self.assertEqual(self.client.post(url, json=pos, headers={"x-driver-key": "wrong"}).status_code, 401)
        self.assertEqual(self.client.post(url, json={"lat": 999, "lng": 0}, headers={"x-driver-key": "demo-key-A1"}).status_code, 400)
        self.assertEqual(self.client.post(url, json=pos, headers={"x-driver-key": "demo-key-A1"}).status_code, 200)
        buses = self.client.get("/api/buses").get_json()
        self.assertTrue(next(b for b in buses if b["label"] == "A1")["online"])
        me = self.client.get("/api/me", headers=self.login("arun@campus.test")).get_json()
        self.assertEqual(me["trips"][0]["buses"][0]["bus"], "A1")

    def test_admin_only_can_add_routes(self):
        route = {"name": "Test", "departure_time": "08:00", "return_time": "17:00",
                 "stops": [{"name": "A", "lat": 1, "lng": 1, "minutes_from_start": 0}, {"name": "College", "lat": 1.1, "lng": 1.1, "minutes_from_start": 30}]}
        self.assertEqual(self.client.post("/api/admin/routes", json=route, headers=self.login("arun@campus.test")).status_code, 403)
        r = self.client.post("/api/admin/routes", json=route, headers=self.login("admin@campus.test", "admin123"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["arrival_time"], "08:30")

    def test_demo_people_counts_and_links(self):
        with conn() as c:
            count = lambda role: c.execute("SELECT COUNT(*) FROM users WHERE role = ?", (role,)).fetchone()[0]
            self.assertEqual((count("student"), count("teacher"), count("parent")), (5, 4, 6))
        # Karthik has two parents; Kavitha follows two children (Priya and Rahul)
        for email in ("ramesh@campus.test", "meena@campus.test"):
            trips = self.client.get("/api/me", headers=self.login(email)).get_json()["trips"]
            self.assertEqual([t["person"] for t in trips], ["Karthik (student)"])
        kids = self.client.get("/api/me", headers=self.login("kavitha@campus.test")).get_json()["trips"]
        self.assertEqual(sorted(t["person"] for t in kids), ["Priya (student)", "Rahul (student)"])

    def test_new_teacher_and_student_trips(self):
        t = self.client.get("/api/me", headers=self.login("venkatesh@campus.test")).get_json()["trips"][0]
        self.assertEqual((t["boarding_stop"]["name"], t["morning_pickup_time"]), ("Kodambakkam", "07:00"))
        t = self.client.get("/api/me", headers=self.login("rahul@campus.test")).get_json()["trips"][0]
        self.assertEqual((t["boarding_stop"]["name"], t["minutes_to_college"]), ("Tambaram", 24))

    def test_frontend_is_served(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/dashboard.html").status_code, 200)
        self.assertEqual(self.client.get("/app.js").status_code, 200)


if __name__ == "__main__":
    unittest.main()

'''


if __name__ == "__main__":
    main()