"""
main.py

Student Management System, backed by real PostgreSQL on Neon - built the
exact same way your class built databaseops.py: SessionLocal() per request,
session.execute(text(...)) with named :placeholders, try/finally to always
close the session, dict(row._mapping) to turn a raw row into clean JSON.

Extended beyond what class covered (students only, single-field PATCH, no
DELETE) to also handle courses and enrollments, general PATCH updates, and
DELETE - since that's what today's task actually asks for.
"""

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models import (
    StudentCreate, StudentUpdate,
    CourseCreate, CourseUpdate,
    EnrollmentCreate, EnrollmentUpdate,
)

app = FastAPI(title="Student Management System - Neon PostgreSQL")


# =================================================================
# STUDENTS
# =================================================================

@app.post("/students")
def create_student(student: StudentCreate):
    session = SessionLocal()
    try:
        result = session.execute(
            text("""
                INSERT INTO students (name, email, age, city)
                VALUES (:name, :email, :age, :city)
                RETURNING id, name, email, age, city, created_at
            """),
            student.model_dump()
        )
        row = result.fetchone()
        session.commit()
        return {"message": "Student created successfully", "student": dict(row._mapping)}

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="A student with this email already exists.")

    finally:
        session.close()


@app.get("/students")
def get_students():
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT * FROM students"))
        students = result.fetchall()
        return [dict(row._mapping) for row in students]
    finally:
        session.close()


@app.get("/students/{student_id}")
def get_student_by_id(student_id: int):
    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT * FROM students WHERE id = :id"), {"id": student_id}
        )
        student = result.fetchone()
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")
        return dict(student._mapping)
    finally:
        session.close()


@app.patch("/students/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    session = SessionLocal()
    try:
        existing = session.execute(
            text("SELECT * FROM students WHERE id = :id"), {"id": student_id}
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Student not found")

        update_data = student.model_dump(exclude_unset=True)
        if not update_data:
            return dict(existing._mapping)

        set_clause = ", ".join(f"{col} = :{col}" for col in update_data.keys())
        update_data["id"] = student_id

        result = session.execute(
            text(f"""
                UPDATE students SET {set_clause}
                WHERE id = :id
                RETURNING id, name, email, age, city, created_at
            """),
            update_data
        )
        row = result.fetchone()
        session.commit()
        return {"message": "Student updated successfully", "student": dict(row._mapping)}

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="A student with this email already exists.")

    finally:
        session.close()


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    session = SessionLocal()
    try:
        result = session.execute(
            text("DELETE FROM students WHERE id = :id RETURNING id"), {"id": student_id}
        )
        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Student not found")
        session.commit()
        return {"message": f"Student {student_id} deleted (their enrollments were deleted too)"}
    finally:
        session.close()


# =================================================================
# COURSES
# =================================================================

@app.post("/courses")
def create_course(course: CourseCreate):
    session = SessionLocal()
    try:
        result = session.execute(
            text("""
                INSERT INTO courses (title, instructor, price, duration)
                VALUES (:title, :instructor, :price, :duration)
                RETURNING *
            """),
            course.model_dump()
        )
        row = result.fetchone()
        session.commit()
        return {"message": "Course created successfully", "course": dict(row._mapping)}
    finally:
        session.close()


@app.get("/courses")
def get_courses():
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT * FROM courses"))
        courses = result.fetchall()
        return [dict(row._mapping) for row in courses]
    finally:
        session.close()


@app.get("/courses/{course_id}")
def get_course_by_id(course_id: int):
    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT * FROM courses WHERE id = :id"), {"id": course_id}
        )
        course = result.fetchone()
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")
        return dict(course._mapping)
    finally:
        session.close()


@app.patch("/courses/{course_id}")
def update_course(course_id: int, course: CourseUpdate):
    session = SessionLocal()
    try:
        existing = session.execute(
            text("SELECT * FROM courses WHERE id = :id"), {"id": course_id}
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Course not found")

        update_data = course.model_dump(exclude_unset=True)
        if not update_data:
            return dict(existing._mapping)

        set_clause = ", ".join(f"{col} = :{col}" for col in update_data.keys())
        update_data["id"] = course_id

        result = session.execute(
            text(f"UPDATE courses SET {set_clause} WHERE id = :id RETURNING *"),
            update_data
        )
        row = result.fetchone()
        session.commit()
        return {"message": "Course updated successfully", "course": dict(row._mapping)}
    finally:
        session.close()


@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    session = SessionLocal()
    try:
        result = session.execute(
            text("DELETE FROM courses WHERE id = :id RETURNING id"), {"id": course_id}
        )
        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Course not found")
        session.commit()
        return {"message": f"Course {course_id} deleted (its enrollments were deleted too)"}
    finally:
        session.close()


# =================================================================
# ENROLLMENTS
# =================================================================

@app.post("/enrollments")
def create_enrollment(enrollment: EnrollmentCreate):
    session = SessionLocal()
    try:
        student = session.execute(
            text("SELECT id FROM students WHERE id = :id"), {"id": enrollment.student_id}
        ).fetchone()
        if student is None:
            raise HTTPException(status_code=404, detail="Student not found")

        course = session.execute(
            text("SELECT id FROM courses WHERE id = :id"), {"id": enrollment.course_id}
        ).fetchone()
        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        result = session.execute(
            text("""
                INSERT INTO enrollments (student_id, course_id)
                VALUES (:student_id, :course_id)
                RETURNING *
            """),
            enrollment.model_dump()
        )
        row = result.fetchone()
        session.commit()
        return {"message": "Enrollment created successfully", "enrollment": dict(row._mapping)}

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="This student is already enrolled in this course.")

    finally:
        session.close()


@app.get("/enrollments")
def get_enrollments():
    """
    Joined with students and courses so the response shows readable names,
    not just three bare ID numbers - same JOIN idea as the course_revenue
    endpoint below, applied to a plain listing instead of an aggregation.
    """
    session = SessionLocal()
    try:
        result = session.execute(text("""
            SELECT
                e.id AS enrollment_id,
                s.id AS student_id,
                s.name AS student_name,
                c.id AS course_id,
                c.title AS course_title,
                e.status,
                e.enrolled_at
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
            ORDER BY e.id
        """))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
    finally:
        session.close()


@app.patch("/enrollments/{enrollment_id}")
def update_enrollment(enrollment_id: int, enrollment: EnrollmentUpdate):
    session = SessionLocal()
    try:
        existing = session.execute(
            text("SELECT id FROM enrollments WHERE id = :id"), {"id": enrollment_id}
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        update_data = enrollment.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided to update.")

        result = session.execute(
            text("UPDATE enrollments SET status = :status WHERE id = :id RETURNING *"),
            {"status": update_data["status"], "id": enrollment_id}
        )
        row = result.fetchone()
        session.commit()
        return {"message": "Enrollment updated successfully", "enrollment": dict(row._mapping)}
    finally:
        session.close()


@app.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: int):
    session = SessionLocal()
    try:
        result = session.execute(
            text("DELETE FROM enrollments WHERE id = :id RETURNING id"), {"id": enrollment_id}
        )
        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        session.commit()
        return {"message": f"Enrollment {enrollment_id} deleted"}
    finally:
        session.close()


# =================================================================
# BONUS: the exact revenue endpoint built live in class
# =================================================================

@app.get("/course_revenue")
def course_revenue():
    session = SessionLocal()
    try:
        query = """
        SELECT
            c.id,
            c.title,
            c.price,
            COUNT(e.id) AS total_students,
            c.price * COUNT(e.id) AS revenue
        FROM courses c
        LEFT JOIN enrollments e
            ON c.id = e.course_id
        WHERE e.status = 'active'
        GROUP BY
            c.id,
            c.title,
            c.price
        ORDER BY revenue DESC;
        """
        result = session.execute(text(query))
        rows = result.fetchall()

        return [
            {
                "course_id": row[0],
                "course_name": row[1],
                "price": float(row[2]),
                "total_students": row[3],
                "revenue": float(row[4])
            }
            for row in rows
        ]
    finally:
        session.close()
