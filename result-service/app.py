from fastapi import FastAPI

app = FastAPI(title="Result Service")

results = {
    101: [
        {"course": "CS301", "grade": "A", "marks": 88},
        {"course": "CS302", "grade": "A+", "marks": 94},
        {"course": "AI301", "grade": "B+", "marks": 79},
    ],
    102: [
        {"course": "AI301", "grade": "A", "marks": 86},
        {"course": "AI302", "grade": "A+", "marks": 91},
    ],
    103: [
        {"course": "EC301", "grade": "B+", "marks": 78},
        {"course": "EC302", "grade": "A", "marks": 84},
    ],
}

@app.get("/")
def root():
    return {"service": "result-service", "status": "running"}

@app.get("/results/{student_id}")
def get_results(student_id: int):
    student_results = results.get(student_id, [])
    average = (
        round(sum(item["marks"] for item in student_results) / len(student_results), 2)
        if student_results else 0
    )
    return {
        "student_id": student_id,
        "results": student_results,
        "average_marks": average
    }
