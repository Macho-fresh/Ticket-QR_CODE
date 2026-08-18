from locust import HttpUser, task, between


class TicketQRUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_events(self):
        self.client.get("/api/view-events/")