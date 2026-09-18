# Student Management System — Neon PostgreSQL Edition

## ⚠️ Before anything else: rotate your credentials

The files you were working from earlier had a real Neon password and a real
MongoDB password hardcoded in plain text. If you haven't already, go rotate
both right now from your Neon and MongoDB Atlas dashboards. A password that
was ever pasted somewhere outside your own machine should be treated as
compromised, full stop.

## 1. Set up Neon and create your tables

1. Log into Neon, open the SQL editor (same one from class).
2. Run the entire contents of `schema.sql` to create `students`, `courses`,
   and `enrollments`, with proper primary keys, foreign keys, constraints,
   and timestamps.

## 2. Set up your `.env` file

```bash
cp .env.example .env
```
Paste your real (freshly-rotated) Neon connection string into `.env`.
**Never** paste it into `.env.example`, or any file that isn't `.env` itself.
`.gitignore` already excludes `.env` from Git.

## 3. Install and run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Open **http://127.0.0.1:8000/docs** to try every endpoint.

## 4. Proving persistence across a restart (for your video)

1. `POST /students` to create one.
2. `GET /students` — confirm it's there.
3. Fully kill the server (not just Ctrl+C and instantly restart — actually
   stop the process, e.g. close the terminal or `pkill -f uvicorn`).
4. Start it again: `uvicorn main:app --reload`.
5. `GET /students` again — same student, same `created_at` timestamp. It
   was never sitting in Python memory — it's been in Neon the whole time.

## What's the same as class, what's new

| From your class (`databaseops.py`) | This version |
|---|---|
| `DATABASE_URL` hardcoded directly in the file | Loaded from `.env` via `python-dotenv` |
| Only a `students` table | `students`, `courses`, `enrollments`, with foreign keys between them |
| Single-field PATCH (`/students/{id}/city`, plain query param) | General PATCH on any field, using `exclude_unset=True` |
| No DELETE endpoint | DELETE added for students, courses, and enrollments |
| No duplicate-data handling | `IntegrityError` caught for duplicate email / duplicate enrollment |
| `course_revenue` endpoint | Kept exactly as built in class (`LEFT JOIN` + `GROUP BY` + status filter) |

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/students` | Create a student |
| GET | `/students` | List all students |
| GET | `/students/{id}` | Get one student |
| PATCH | `/students/{id}` | Update any subset of a student's fields |
| DELETE | `/students/{id}` | Delete a student (cascades to their enrollments) |
| POST | `/courses` | Create a course |
| GET | `/courses` | List all courses |
| GET | `/courses/{id}` | Get one course |
| PATCH | `/courses/{id}` | Update any subset of a course's fields |
| DELETE | `/courses/{id}` | Delete a course (cascades to its enrollments) |
| POST | `/enrollments` | Enroll a student in a course |
| GET | `/enrollments` | View all enrollments (joined with names/titles) |
| PATCH | `/enrollments/{id}` | Update an enrollment's status |
| DELETE | `/enrollments/{id}` | Remove an enrollment |
| GET | `/course_revenue` | The exact revenue report built live in class |
