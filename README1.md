# Student Management Microservices

## 1. Project Overview
This project implements a Student Management System using a microservices architecture. It demonstrates how monolithic applications can be broken down into smaller, loosely coupled, and independently deployable services. By using microservices, the application achieves better scalability, fault isolation, and maintainability.

## 2. Aim
To Build → Deploy → Analyze a Containerized Microservice Application Under Varying Workloads.

## 3. Objectives
- Developing 3 independent microservices (Student, Course, Result).
- Creating REST APIs using FastAPI.
- Docker containerization for each service.
- Docker Compose deployment to orchestrate multiple containers.
- Docker networking for seamless container-to-container communication.
- Inter-service communication via HTTP requests.
- Workload testing using Locust.
- CPU and memory monitoring using Docker stats.
- Performance analysis under varying workload levels.

## 4. System Architecture
The system consists of a Client communicating with the Student Service, which in turn aggregates data from the Course Service and Result Service.

```text
Client
   ↓
Student Service
   ├──→ Course Service
   └──→ Result Service
```

- **Student Service**: Acts as the main entry point and orchestrator. It manages student profiles and provides a consolidated dashboard.
- **Course Service**: Manages the courses enrolled by students.
- **Result Service**: Manages the grades/marks of the students.
When a client requests a student's dashboard, the Student Service fetches the student's profile, makes asynchronous HTTP requests to both Course and Result services, and aggregates the responses into a single JSON response.

## 5. Technologies Used
| Technology | Purpose |
|------------|---------|
| Python 3.12 | Core programming language |
| FastAPI | Framework for building REST APIs |
| Uvicorn | ASGI web server for FastAPI |
| Docker | Containerizing the microservices |
| Docker Compose | Orchestrating multi-container deployment |
| HTTPX | Asynchronous HTTP client for inter-service communication |
| Locust | Workload and performance testing |

## 6. Microservices

### 6.1 Student Service
- **Responsibility**: Manages student details and acts as an orchestrator by aggregating data from the other two services to serve the dashboard.
- **Port**: 5001
- **APIs**:
  | Method | Endpoint | Description |
  |--------|----------|-------------|
  | GET | `/` | Returns service status |
  | GET | `/students` | Returns all students |
  | GET | `/students/{student_id}` | Returns details of a specific student |
  | GET | `/students/{student_id}/dashboard` | Aggregates and returns student profile, courses, and results |

### 6.2 Course Service
- **Responsibility**: Manages courses registered by students.
- **Port**: 5002
- **APIs**:
  | Method | Endpoint | Description |
  |--------|----------|-------------|
  | GET | `/` | Returns service status |
  | GET | `/courses` | Returns all available courses |
  | GET | `/courses/student/{student_id}` | Returns courses for a specific student |

### 6.3 Result Service
- **Responsibility**: Manages student marks and calculates the average marks.
- **Port**: 5003
- **APIs**:
  | Method | Endpoint | Description |
  |--------|----------|-------------|
  | GET | `/` | Returns service status |
  | GET | `/results/{student_id}` | Returns grades, marks, and calculated `average_marks` for a student |

## 7. Running the Application Locally
You can run a service independently (e.g., Student Service) assuming its dependencies are mocked or running:
```bash
cd student-service
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5001
```

## 8. Docker Containerization
Each service contains a `Dockerfile` based on `python:3.12-slim`.
- **Base image**: `python:3.12-slim` (lightweight OS and Python environment).
- **Working directory**: `WORKDIR /app` sets the working directory inside the container.
- **Dependency installation**: `COPY requirements.txt .` and `RUN pip install --no-cache-dir -r requirements.txt` installs packages.
- **Application copy**: `COPY app.py .` copies the source code.
- **Exposed port**: `EXPOSE 5001` (or 5002/5003) documents the listening port.
- **Startup command**: `CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]` runs the server.

Important Docker Commands:
- `docker --version`: Checks Docker version.
- `docker images`: Lists available local images.
- `docker build -t <image_name> .`: Builds a Docker image from a Dockerfile.
- `docker ps`: Lists running containers.
- `docker ps -a`: Lists all containers (running and stopped).
- `docker run -p <host_port>:<container_port> <image>`: Runs a container.
- `docker logs <container_id>`: Views logs of a container.
- `docker stop <container_id>`: Stops a running container.
- `docker start <container_id>`: Starts a stopped container.
- `docker rm <container_id>`: Removes a stopped container.

## 9. Docker Compose
The `docker-compose.yml` file builds and deploys all 3 services together.
- `docker compose build`: Builds images for all services defined.
- `docker compose up -d`: Starts all services in detached (background) mode.
- `docker compose ps`: Lists containers managed by the compose file.
- `docker compose logs`: Shows aggregated logs for all services.
- `docker compose down`: Stops and removes the containers and networks.

## 10. Docker Network
The `docker-compose.yml` configures a custom bridge network `microservice-net`.
- **Why a common network**: Allows containers to discover and communicate with each other securely.
- **Communication**: Containers communicate using their service names acting as hostnames (e.g., `http://course-service:5002`).
- **Why not localhost**: Inside a container, `localhost` refers to the container itself, not the host machine or other containers. Service names are resolved by Docker's internal DNS.

## 11. Inter-Service Communication
Request flow for `GET /students/101/dashboard`:
```text
Client
↓ (GET /students/101/dashboard)
Student Service
↓ (GET http://course-service:5002/courses/student/101)
Course Service
↓
Result Service (GET http://result-service:5003/results/101)
↓
Student Service (Aggregates JSON from all responses)
↓
Client
```
The Student Service uses asynchronous `httpx` to call the Course and Result services concurrently, combining the responses into a single unified JSON object.

## 12. Workload Testing
Workload testing is implemented using `Locust` (`locustfile.py`).
- **Endpoint tested**: `GET /students/101/dashboard`
- **Workload levels**:
  - W1 = 1 concurrent user
  - W2 = 2 concurrent users
  - W3 = 4 concurrent users
  - W4 = 8 concurrent users
  - W5 = 16 concurrent users
- **Concurrency**: Simulated by Locust users making continuous requests.
- **Duration**: Handled by the experiment script running Locust for a set duration per workload.
- **Metrics collected**: Total requests, failed requests, response time, and throughput (requests per second).

## 13. Resource Monitoring
Docker resource usage is collected using `docker stats`.
- `docker stats`: Provides a live stream of container resource usage.
- `docker stats --no-stream`: Captures a single snapshot of resource usage.
- **CPU utilization**: Percentage of host CPU used by the container.
- **Memory utilization**: Amount of RAM used and its percentage.

## 14. Performance Results

| Workload | Concurrency | Total Requests | Average Response Time (ms) | Throughput (req/s) | Failed Requests | Student Avg CPU (%) | Course Avg CPU (%) | Result Avg CPU (%) | Student Avg Memory (MiB) | Course Avg Memory (MiB) | Result Avg Memory (MiB) |
|----------|-------------|----------------|----------------------------|--------------------|-----------------|---------------------|--------------------|--------------------|--------------------------|-------------------------|-------------------------|
| W1       | 1           | 122            | 28.0                       | 4.19               | 0               | 6.96                | 0.66               | 0.58               | 94.57                    | 30.11                   | 29.91                   |
| W2       | 2           | 247            | 33.0                       | 8.59               | 0               | 15.39               | 1.04               | 1.44               | 94.91                    | 30.19                   | 30.10                   |
| W3       | 4           | 430            | 47.0                       | 14.77              | 0               | 25.24               | 1.60               | 1.46               | 95.10                    | 29.97                   | 29.91                   |
| W4       | 8           | 830            | 60.0                       | 28.30              | 0               | 36.34               | 2.60               | 2.72               | 95.05                    | 30.22                   | 30.08                   |
| W5       | 16          | 1286           | 152.0                      | 43.48              | 0               | 47.34               | 3.21               | 3.99               | 94.52                    | 30.37                   | 30.57                   |

## 15. Performance Graphs
- **concurrent_vs_response_time.png**: X-axis (Concurrency), Y-axis (Response Time in ms). Shows response time increasing gradually, with a sharp spike at W5 (16 users).
- **concurrent_vs_throughput.png**: X-axis (Concurrency), Y-axis (Throughput in req/s). Throughput increases almost linearly with concurrency up to 16 users.
- **cpu_per_service.png**: X-axis (Workload/Concurrency), Y-axis (CPU %). Shows the Student Service consumes significantly more CPU than Course/Result services.
- **memory_per_service.png**: X-axis (Workload/Concurrency), Y-axis (Memory). Shows memory consumption remains relatively flat across workloads for all services.
- **concurrent_vs_cpu.png**: Shows overall CPU scaling with concurrency.
- **concurrent_vs_memory.png**: Shows overall memory scaling with concurrency.

## 16. Performance Analysis
1. **How does response time change with increasing concurrency?** It increases, with a significant jump from 60ms to 152ms at 16 concurrent users.
2. **How does throughput change?** Throughput scales up with concurrency, peaking at 43.48 req/s at 16 users.
3. **Are there failed requests?** No, 0 failed requests across all workloads.
4. **Which service consumes the most CPU?** The Student Service (peaks at ~79%, avg 47% at W5).
5. **Which service consumes the most memory?** The Student Service (~95 MiB on average).
6. **How does CPU change with workload?** CPU utilization increases proportionally with concurrency, especially for the Student Service.
7. **How does memory change with workload?** Memory utilization remains mostly stable and flat regardless of the workload.
8. **At what workload does performance degradation become noticeable?** At W5 (16 concurrent users), average response time spikes heavily.
9. **Are there response-time outliers?** Yes, max response times hit 1836ms at W3, showing occasional spikes.
10. **What is the overall bottleneck?** The Student Service, as it handles incoming traffic, outgoing concurrent requests, and JSON aggregation.
11. **What is the overall performance conclusion?** The microservices handle scaling well up to a point, but the API gateway/orchestrator (Student Service) requires optimization or scaling first.

## 17. Project Structure
```text
.
├── docker-compose.yml
├── locustfile.py
├── process_results.py
├── run_experiment.py
├── student-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── course-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── result-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── experiment_results/
│   ├── performance_results.csv
│   └── resource_observations.csv
└── results/
    ├── analysis.md
    ├── final_observation_table.csv
    ├── performance_results.csv
    ├── resource_observations.csv
    └── graphs/
        ├── concurrent_vs_cpu.png
        ├── concurrent_vs_memory.png
        ├── concurrent_vs_response_time.png
        ├── concurrent_vs_throughput.png
        ├── cpu_per_service.png
        └── memory_per_service.png
```

## 18. Checkpoint-wise Evaluation Mapping
- **Checkpoint 1 — Design and Develop 3 Microservices**: Implemented 3 independent FastAPI apps (`student-service/app.py`, `course-service/app.py`, `result-service/app.py`). Demonstrated by running them locally.
- **Checkpoint 2 — Containerize and Deploy**: Created `Dockerfile` for each service and a `docker-compose.yml`. Demonstrated via `docker compose up -d`.
- **Checkpoint 3 — Establish and Demonstrate Inter-Service Communication**: Student Service uses `httpx` to call Course and Result services. Demonstrated by hitting `/students/101/dashboard`.
- **Checkpoint 4 — Generate Varying Workloads and Monitor Performance**: Used `locustfile.py` and `run_experiment.py` to generate W1 to W5 workloads while collecting `docker stats`.
- **Checkpoint 5 — Analyze and Present Results**: Used `process_results.py` to generate graphs and the final CSV table mapping metrics against workloads.

## 19. Complete Execution Workflow
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

## 20. Important Docker Commands — Quick Reference
| Command | Purpose |
|---------|---------|
| `docker build -t name .` | Builds an image from a Dockerfile |
| `docker run -p 5001:5001 img`| Runs a container and maps the port |
| `docker compose build` | Builds all services in compose file |
| `docker compose up -d` | Starts all services in background |
| `docker compose down` | Stops and removes compose containers |
| `docker stats` | Streams live CPU/Memory utilization |
| `docker logs <container>` | Views output of a container |



## 21. Conclusion
The project successfully demonstrates the build, deployment, and performance analysis of a containerized microservice application. Workload testing revealed that the system scales effectively up to 8 concurrent users, after which the Student Service (acting as the aggregator) becomes the bottleneck, exhibiting high CPU utilization and spiked response times. Memory usage remains highly stable across all services regardless of the load.
