from fastapi import FastAPI

app = FastAPI(title="Course Service")

courses = {
    101: [
        {"code": "CS301", "name": "Data Structures", "credits": 4},
        {"code": "CS302", "name": "Operating Systems", "credits": 4},
        {"code": "AI301", "name": "Machine Learning", "credits": 3},
    ],
    102: [
        {"code": "AI301", "name": "Machine Learning", "credits": 3},
        {"code": "AI302", "name": "Deep Learning", "credits": 4},
    ],
    103: [
        {"code": "EC301", "name": "Digital Signal Processing", "credits": 4},
        {"code": "EC302", "name": "Computer Networks", "credits": 3},
    ],
}

@app.get("/")
def root():
    return {"service": "course-service", "status": "running"}

@app.get("/courses")
def get_courses():
    all_courses = []
    for student_courses in courses.values():
        all_courses.extend(student_courses)
    return all_courses

@app.get("/courses/student/{student_id}")
def get_student_courses(student_id: int):
    return {
        "student_id": student_id,
        "courses": courses.get(student_id, [])
    }
