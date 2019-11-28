class Waiter:
    def __init__(self, tasks_count):
        self.tasks_count = tasks_count

    def task_done(self):
        self.tasks_count -= 1

    def __await__(self):
        while self.tasks_count > 0:
            yield


class interrupt:
    def __await__(self):
        yield
