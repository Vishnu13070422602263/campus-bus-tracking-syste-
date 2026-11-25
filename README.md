# campus-bus-tracking-system


# 🚌 Campus Bus Tracking System

A web app that helps college **students, teachers and parents** track the college bus: where it starts, every stop with its planned time, the total journey duration, and where the bus is right now.

Built for a college in **Pallavaram, Chennai**, with a sample route from **Chennai Beach** along the local-line stations to the campus.

## Why I built this

Students often wait at stops without knowing if the bus is late, and parents have no way to know if their child's bus is on its way. This project gives everyone one place to see the bus schedule and live location.

## Features

- **Route details:** start point, end point, departure and arrival time, total journey duration and number of stops
- **Stop timetable:** every stop with its planned time, with your own stop highlighted
- **Live bus tracking** on a map (Leaflet + OpenStreetMap), with minutes until the bus reaches your stop
- **Morning and evening trips:** to college and back home
- **Role-based logins:** student, teacher, parent and admin
- **Parent access with a family code:** a parent signs up with their child's email and the code from the child's dashboard, so a stranger cannot track a student
- **Driver page:** the driver's phone shares its GPS location
- **Admin API:** add new routes and buses
- **Automated tests** for schedules, logins and permissions

## Tech stack

| Part | Technology |
|---|---|
| Backend | Python, Flask (REST API) |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Map | Leaflet, OpenStreetMap |

## How to run

Requires Python 3.9 or newer.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m backend.seed           # load sample routes, buses and demo users
python app.py                    # open http://localhost:5000
python -m backend.simulate       # second terminal: fake GPS so buses move
```

Run the tests with `python -m unittest discover -s tests`.

## Demo logins

All demo passwords are `demo123` and emails end in `@campus.test`.

| Role | Try |
|---|---|
| Student | `arun`, `priya`, `karthik`, `divya`, `rahul` |
| Teacher | `lakshmi`, `venkatesh`, `fathima`, `rajan` |
| Parent | `parent`, `ramesh`, `meena`, `suresh`, `kavitha`, `anitha` |
| Admin | `admin` (password `admin123`) |

Pages: `/` live map, `/login.html` sign in, `/dashboard.html` my bus, `/driver.html` driver.

## Project structure

```
app.py          Flask app and API routes
backend/        Database, login, schedule and ETA logic, sample data, GPS simulator
public/         HTML, CSS and JavaScript pages
tests/          Automated tests
```

## Limitations

- Stop locations and timings are approximate samples. Replace them in `backend/seed.py` with your real route.
- Live arrival time is a straight-line estimate and does not follow roads.
- Demo passwords and driver keys are for testing only. Change them before any real use.

## Future improvements

- SMS or push alerts when the bus is near your stop
- Delay notices from the driver
- More accurate arrival times using road distance
- Admin web page for managing routes

## License

MIT


