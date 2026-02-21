from locust import HttpUser, task, between

class IT_Student(HttpUser):
    wait_time = between(1, 3) # Имитация раздумий пользователя

    @task(5)
    def view_main_plan(self):
        """Самый тяжелый запрос с вложенными дисциплинами"""
        self.client.get("/directions-with-disciplines")

    @task(2)
    def view_teachers(self):
        self.client.get("/teachers")

    @task(1)
    def view_admin_login(self):
        """Проверка доступности админки (sqladmin)"""
        self.client.get("/admin/login")