from locust import HttpUser, task, between


class StudentDashboardUser(HttpUser):
    wait_time = between(0.1, 0.3)

    @task
    def student_dashboard(self):
        self.client.get(
            "/students/101/dashboard",
            name="GET /students/101/dashboard"
        )