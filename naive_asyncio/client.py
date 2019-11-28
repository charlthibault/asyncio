#!/usr/bin/env python3

import click

from naive_asyncio.aiosocket import aiosocket
from naive_asyncio.ioloop import sleep, Loop
from naive_asyncio.utils import Waiter


async def client_coro(client, waiter):
    await client.connect(('google.com', 80))
    await client.sendall(b"GET / HTTP/1.1\r\n\r\n")
    msg = await client.recv(4096)
    print(msg.decode())
    waiter.task_done()


async def running_time(waiter):
    count = 0
    while waiter.tasks_count > 0:
        await sleep(0.01)
        count += 1
        print('Running since {} ms'.format(count * 10))


@click.command()
def main():
    client = aiosocket()
    waiter = Waiter(1)
    Loop().run_tasks(client_coro(client, waiter), running_time(waiter))


if __name__ == '__main__':
    main()
