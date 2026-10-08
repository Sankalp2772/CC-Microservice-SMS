# Student Management Microservices

## 1. Project Overview
This project implements a Student Management System using a microservices architecture. It demonstrates how monolithic applications can be broken down into exactly three independent, loosely coupled, and independently deployable services. It was designed to fulfill the requirements of the experiment: "Build, Deploy and Analyze a Containerized Microservice Application Under Varying Workloads."

## 2. Aim & Objectives
**Aim:** To Build → Deploy → Analyze a Containerized Microservice Application Under Varying Workloads.

**Objectives:**
- Develop 3 independent microservices (Student, Course, Result) using FastAPI.
- Containerize each service using Docker.
- Orchestrate deployment with Docker Compose.
- Establish seamless container-to-container communication via a custom Docker network.
- Conduct workload testing using Locust.
- Monitor CPU and memory using Docker stats.
- Analyze performance under varying workload levels.

## 3. System Architecture
A user request to the main dashboard triggers the Student Service, which acts as an orchestrator and retrieves data asynchronously from the Course Service and Result Service before composing the final response.

```text
Client
   ↓
Student Service (Port 5001)
   ├──→ Course Service (Port 5002)
   └──→ Result Service (Port 5003)
```

## 4. Technologies Used
| Technology | Purpose |
|------------|---------|
| Python 3.12 | Core programming language |
| FastAPI | Framework for building REST APIs |
| Uvicorn | ASGI web server |
| Docker | Containerizing the microservices |
| Docker Compose | Orchestrating multi-container deployment |
| HTTPX | Asynchronous HTTP client for inter-service communication |
| Locust | Workload and performance testing |

## 5. Microservices

### 5.1 Student Service
- **Port:** 5001
- **Responsibility:** Handles student information, overall orchestration, and acts as the entry point for end-to-end dashboard requests.
- **APIs:** 
  - `GET /` - Returns service status
  - `GET /students` - Returns all students
  - `GET /students/{student_id}` - Returns specific student details
  - `GET /students/{student_id}/dashboard` - Aggregates student profile, courses, and results

### 5.2 Course Service
- **Port:** 5002
- **Responsibility:** Maintains and provides course information linked to students.
- **APIs:**
  - `GET /` - Returns service status
  - `GET /courses` - Returns all available courses
  - `GET /courses/student/{student_id}` - Returns courses for a specific student

### 5.3 Result Service
- **Port:** 5003
- **Responsibility:** Maintains student results, marks, and grades, calculating averages dynamically.
- **APIs:**
  - `GET /` - Returns service status
  - `GET /results/{student_id}` - Returns grades, marks, and calculated average marks

## 6. Docker Architecture & Network
All three services are fully containerized using individual `Dockerfile` configurations based on `python:3.12-slim`. They are orchestrated simultaneously via `docker-compose.yml`.

The system uses a custom Docker bridge network named `microservice-net`. All three services are attached to this network.

## 7. Inter-Service Communication
The services communicate exclusively over the internal `microservice-net` network using Docker service names, completely bypassing localhost.
- `http://course-service:5002`
- `http://result-service:5003`

Request flow for `GET /students/101/dashboard`:
```text
Client
↓ 
Student Service
↓ (Asynchronous GET to course-service:5002 & result-service:5003)
Course & Result Services
↓
Student Service (Aggregates JSON)
↓
Client
```

## 8. How to Run
```bash
# Build the Docker images
docker compose build

# Start all services in detached mode
docker compose up -d

# Verify containers are running
docker compose ps
```

## 9. Workload Testing & Levels
The API endpoint `/students/101/dashboard` was load-tested using **Locust** (`locustfile.py`). Performance measurements and resource utilization (`docker stats`) were logged simultaneously for the following workloads:
- **W1** = 1 concurrent user
- **W2** = 2 concurrent users
- **W3** = 4 concurrent users
- **W4** = 8 concurrent users
- **W5** = 16 concurrent users

## 10. Performance & Resource Results

Detailed measurements are available in `results/performance_results.csv` and `results/final_observation_table.csv`.

| Workload | Concurrency | Total Requests | Average Response Time (ms) | Throughput (req/s) | Failed Requests | Student Avg CPU (%) | Course Avg CPU (%) | Result Avg CPU (%) | Student Avg Memory (MiB) | Course Avg Memory (MiB) | Result Avg Memory (MiB) |
|----------|-------------|----------------|----------------------------|--------------------|-----------------|---------------------|--------------------|--------------------|--------------------------|-------------------------|-------------------------|
| W1       | 1           | 122            | 28.0                       | 4.19               | 0               | 6.96                | 0.66               | 0.58               | 94.57                    | 30.11                   | 29.91                   |
| W2       | 2           | 247            | 33.0                       | 8.59               | 0               | 15.39               | 1.04               | 1.44               | 94.91                    | 30.19                   | 30.10                   |
| W3       | 4           | 430            | 47.0                       | 14.77              | 0               | 25.24               | 1.60               | 1.46               | 95.10                    | 29.97                   | 29.91                   |
| W4       | 8           | 830            | 60.0                       | 28.30              | 0               | 36.34               | 2.60               | 2.72               | 95.05                    | 30.22                   | 30.08                   |
| W5       | 16          | 1286           | 152.0                      | 43.48              | 0               | 47.34               | 3.21               | 3.99               | 94.52                    | 30.37                   | 30.57                   |

## 11. Performance Graphs

### Concurrent Requests vs Average Response Time
![Concurrent vs Response Time](results/graphs/concurrent_vs_response_time.png)
*Observation: Response time scales gradually until 8 users, then spikes significantly at 16 concurrent users.*

### Concurrent Requests vs Throughput
![Concurrent vs Throughput](results/graphs/concurrent_vs_throughput.png)
*Observation: Throughput increases almost linearly with concurrency up to 16 users, peaking at ~43 req/s.*

### Concurrent Requests vs CPU Utilization
![Concurrent vs CPU Utilization](results/graphs/concurrent_vs_cpu.png)
*Observation: Overall CPU utilization increases proportionally with concurrency.*

### Concurrent Requests vs Memory Utilization
![Concurrent vs Memory Utilization](results/graphs/concurrent_vs_memory.png)
*Observation: Overall memory utilization remains highly stable across all workload levels.*

### Average CPU per Service
![Average CPU per Service](results/graphs/cpu_per_service.png)
*Observation: The Student Service consumes significantly more CPU (up to ~79% peak, 47% average) than the Course or Result services.*

### Average Memory per Service
![Average Memory per Service](results/graphs/memory_per_service.png)
*Observation: The Student Service uses ~95 MiB, while the others use ~30 MiB. Memory remains flat across workloads.*

## 12. Analysis
An in-depth analysis of the system performance reveals:
1. **Bottleneck:** The `student-service` acts as the primary bottleneck during scaling as it handles E2E orchestration, waits for network responses, and parses JSON.
2. **CPU usage:** CPU scales directly with workload, primarily burdening the Student Service.
3. **Memory usage:** Memory proved to be independent of workload, remaining extremely stable.
4. **Degradation:** Performance degradation becomes noticeable at 16 concurrent users, where response time jumps from 60ms to 152ms.

## 13. Complete Execution Workflow
```text
DEVELOP (Write FastAPI code)
↓
CONTAINERIZE (Write Dockerfiles)
↓
BUILD (docker compose build)
↓
DEPLOY (docker compose up -d)
↓
CONNECT (Verify inter-service network calls)
↓
LOAD TEST (python run_experiment.py)
↓
MONITOR (Collect docker stats during test)
↓
ANALYZE (python process_results.py)
↓
DEMONSTRATE (Show CSVs and Graphs)
```

## 14. Checkpoint Status
- **Checkpoint 1 — Design and Develop 3 Microservices**: Implemented 3 independent FastAPI apps.
- **Checkpoint 2 — Containerize and Deploy**: Created `Dockerfile` for each service and deployed via `docker-compose.yml`.
- **Checkpoint 3 — Establish Inter-Service Communication**: Implemented asynchronous `httpx` calls between services via custom Docker network.
- **Checkpoint 4 — Generate Workloads and Monitor**: Executed Locust tests for workloads W1-W5 while capturing `docker stats`.
- **Checkpoint 5 — Analyze Results**: Generated charts, populated CSVs, and formulated the performance conclusions.

## 15. Viva Preparation (Quick Reference)
- **Microservice vs Monolith**: Breaks application into small, independent services vs one large codebase.
- **Why Docker Network?**: Allows isolated containers to communicate securely via internal DNS (service names) without exposing ports unnecessarily.
- **Why Student Service is the bottleneck**: It must wait for both Course and Result services to respond, process their JSON, and serve the final result.
- **docker build vs docker run**: `build` creates the image blueprint; `run` executes it as a container.
- **docker stats**: Streams live metrics for CPU, Memory, and Network I/O.

## 16. Conclusion
The microservices ecosystem functioned correctly without any failed requests. The `student-service` acts as the primary bottleneck during scaling as it handles E2E orchestration and consumes the most CPU. Memory usage remained extremely stable across all services regardless of workload size. The architecture successfully fulfills all experimental objectives.
