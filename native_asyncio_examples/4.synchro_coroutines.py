import asyncio


class Future:
    def __init__(self):
        self.done = False

    def __await__(self):
        while not self.done:
            yield


async def wait_job(waiter):
    print('start')
    await waiter  # wait for count_up_to to be finished
    print('finished')


async def count_up_to(waiter, n):
    for i in range(n):
        print(i)
        await asyncio.sleep(0)
    waiter.done = True


async def main():
    future = Future()

    await asyncio.gather(wait_job(future), count_up_to(future, 1))


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
