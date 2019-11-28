import functools
import time

from naive_asyncio.utils import Waiter


async def gather(*tasks):
    async def task_wrapper(waiter, task):
        await task
        waiter.task_done()

    _waiter = Waiter(len(tasks))
    wrapper = functools.partial(task_wrapper, _waiter)

    wrapped_tasks = map(wrapper, tasks)
    Loop().add_tasks(*wrapped_tasks)

    await _waiter


class EventHandler:
    def __init__(self, condition, future=None):
        self.condition = condition
        self.future = future if future is not None else Future()

    def schedule_callback(self):
        self.future.done()

    def __await__(self):
        Loop().add_event(self)
        yield self.future

        return self.future.result


def time_event(t):
    done_at = time.time() + t

    def condition():
        return done_at <= time.time()

    return EventHandler(condition=condition)


class Future:
    def __init__(self, callback=None):
        self.result = None
        self._done = False
        self.task = callback or Loop().current_task

    def __await__(self):
        yield self

        assert self._done

    def is_done(self):
        return self._done

    def done(self):
        self._done = True
        if self.task is not None:
            Loop().add_tasks(self.task)


class Loop:
    current = None

    def __new__(cls, *args, **kwargs):
        if cls.current is not None:
            return cls.current
        return super().__new__(cls)

    def __init__(self):
        if self.current is not None:
            return
        Loop.current = self
        self.tasks = []
        self.events = []
        self.current_task = None

    def add_event(self, event: EventHandler):
        self.events.append(event)
        return event.future

    def add_tasks(self, *tasks):
        for task in tasks:
            if hasattr(task, '__await__'):
                task = task.__await__()
            self.tasks.append(task)

    def run_tasks(self, *tasks):
        self.add_tasks(*tasks)
        self.run()

    def _handle_events(self):
        for event in self.events:
            if event.condition():
                event.schedule_callback()
                self.events.remove(event)

    def run(self):
        while self.tasks or self.events:
            self._handle_events()

            if not self.tasks:
                continue

            task = self.tasks.pop(0)
            self.current_task = task
            try:
                result = next(task)
            except StopIteration:
                continue

            # add back task only if does not rely on future
            if not isinstance(result, Future) or result.is_done():
                self.current_task = task
                self.tasks.append(task)


async def sleep(t):
    await time_event(t)


async def foo(count):
    print('before ', count)
    await sleep(count)
    print('after ', count)


if __name__ == '__main__':
    Loop().run_tasks(foo(5), foo(1))
