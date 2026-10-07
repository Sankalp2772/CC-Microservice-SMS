from fastapi import FastAPI
import httpx

app = FastAPI(title="Student Service")

students = {
    101: {"id": 101, "name": "Rahul", "department": "CSE"},
    102: {"id": 102, "name": "Aisha", "department": "AI"},
    103: {"id": 103, "name": "Kiran", "department": "ECE"},
}

COURSE_SERVICE = "http://course-service:5002"
RESULT_SERVICE = "http://result-service:5003"

@app.get("/")
def root():
    return {"service": "student-service", "status": "running"}

@app.get("/students")
def get_students():
    return list(students.values())

@app.get("/students/{student_id}")
def get_student(student_id: int):
    student = students.get(student_id)
    if not student:
        return {"error": "Student not found"}
    return student

@app.get("/students/{student_id}/dashboard")
async def student_dashboard(student_id: int):
    student = students.get(student_id)
    if not student:
        return {"error": "Student not found"}

    async with httpx.AsyncClient(timeout=5.0) as client:
        course_response = await client.get(
            f"{COURSE_SERVICE}/courses/student/{student_id}"
        )
        result_response = await client.get(
            f"{RESULT_SERVICE}/results/{student_id}"
        )

    return {
        "student": student,
        "courses": course_response.json(),
        "results": result_response.json(),
    }
